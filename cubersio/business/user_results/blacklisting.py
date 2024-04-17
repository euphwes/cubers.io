
from arrow import now

from cubersio import app
from cubersio.util.events.mbld import MbldSolve
from cubersio.persistence.comp_manager import get_comp_event_name_by_id

# -------------------------------------------------------------------------------------------------

__TIMESTAMP_FORMAT = 'YYYY-MM-DD'

# Threshold breached blacklist note
__AUTO_BLACKLIST_NOTE_TEMPLATE = "Results automatically hidden on {date} because the user's {type} is "
__AUTO_BLACKLIST_NOTE_TEMPLATE += "less than the threshold for this event."

# Permanent blacklist note
__PERMA_BLACKLIST_NOTE_TEMPLATE = "Results automatically hidden on {date} because this user is flagged for "
__PERMA_BLACKLIST_NOTE_TEMPLATE += "permanent blacklist."

# MBLD blacklist note
__MBLD_BLACKLIST_NOTE_TEMPLATE = "Results automatically hidden on {date} because this result has {points} "
__MBLD_BLACKLIST_NOTE_TEMPLATE += "points, which is higher than the threshold."

# For retrieving blacklist threshold multiplicative factor from app config
__KEY_AUTO_BL_FACTOR = 'AUTO_BL_FACTOR'

# Values to be inserted into blacklist note templates above, and key for a kwargs dict
# to insert timestamp as `date` kwarg
__SINGLE   = 'single'
__AVERAGE  = 'average'
__KEY_DATE = 'date'

# Dictionary of event name to tuple of (WR single, WR average) in centiseconds
# WCA WRs as of 10 Jan 2022
__AUTO_BLACKLIST_THRESHOLDS = {
    '2x2':           (43, 92),
    '3x3':           (313, 448),
    '4x4':           (1686, 1938),
    '5x5':           (3252, 3594),
    '6x6':           (5974, 6646),
    '7x7':           (9568, 10178),
    '3BLD':          (1200, 1415),
    '4BLD':          (5787, 6876),
    '5BLD':          (14162, 14763),
    'Square-1':      (341, 491),
    'Clock':         (200, 250),
    '3x3OH':         (620, 862),
    'Pyraminx':      (73, 143),
    'Megaminx':      (2318, 2684),
    'Skewb':         (75, 153),
    'FMC':           (1600, 2100),  # in "centi-moves"
    '3x3 With Feet': (1696, 2222),
    'MBLD':          59,            # points

    # "Reasonable values" sourced from
    # https://www.speedsolving.com/wiki/index.php/List_of_Unofficial_World_Records
    # with a little wiggle room. Events which aren't there are based on times that have been
    # submitted to the site over the months before the auto-blacklist concept was implemented.
    'Kilominx':        (1400, 1600),
    '2BLD':            (350, 450),
    'Redi Cube':       (200, 580),
    'Dino Cube':       (198, 400),
    'Void Cube':       (500, 700),
    '4x4 OH':          (4500, 5000),
    'BiCube':          (250, 700),
    '2x2x3':           (50, 90),
    '3x3x2':           (250, 400),
    '3x3x4':           (1400, 2000),
    '3x3x5':           (3500, 4000),
    '2GEN':            (150, 250),
    'F2L':             (175, 275),
    '2-3-4 Relay':     (3200, 1),
    '3x3 Relay of 3':  (2000, 1),
    'PLL Time Attack': (2200, 1),
    '8x8':             (21000, 1),
    '9x9':             (31500, 1),
    '10x10':           (42000, 1),
    '15 Puzzle':       (125, 250),
    'FTO':             (1000, 1400),
    'Rex Cube':        (3200, 4000),
    '3x3 Mirror Blocks/Bump': (800, 1100)
}

# -------------------------------------------------------------------------------------------------
# Functions and types below are intended to be used directly.
# -------------------------------------------------------------------------------------------------

def take_blacklist_action_if_necessary(results, user):
    """ Determines if this UserEventResults should be auto-blacklisted because of an absurdly low
    time. Uses a multiplicative factor of the current world records as a threshold, which is
    adjustable by environment variable. """

    # If the results aren't complete, return early since we don't need to blacklist yet
    if not results.is_complete:
        return __ensure_clean_unblacklisted(results), False

    # Check if the user is flagged to have all of their results automatically blacklisted
    if user.always_blacklist:
        return __perform_perma_blacklist_action(results, user), True

    # Get comp event name
    comp_event_name = get_comp_event_name_by_id(results.comp_event_id)

    # Get the auto-blacklist thresholds for the event these results are for.
    # If we don't have thresholds, leave without taking any blacklist action
    thresholds = __get_event_thresholds(comp_event_name)
    if not thresholds:
        return results, False

    # First check if results are for MBLD, because that blacklisting check is a little different
    # We're only checking single, and we need to convert the 'time' (encoded value) into MBLD points
    # so we can compare it against the MBLD points threshold
    if comp_event_name == 'MBLD':
        user_points = MbldSolve(results.single).points
        if user_points < thresholds:
            return __ensure_clean_unblacklisted(results), False
        return __blacklist_results_with_note(results, __MBLD_BLACKLIST_NOTE_TEMPLATE, points=user_points), True

    # Extract the adjusted single and average thresholds
    single_threshold, average_threshold = thresholds

    # If the average threshold has been breached, it's more likely that the user is
    # intentionally posting bogus times. Blacklist this set of results, add a
    # WeeklyBlacklist record to indicate that other results posted this week are to be
    # automatically blacklisted, and fire off a task to retroactively blacklist other results
    # already posted this week.
    if __check_event_average_threshold_breached(results, average_threshold):
        return __perform_average_results_blacklist_action(results, user), True

    # If the single threshold has been breached, blacklist just the one set of results.
    # We don't want to go overboard and blacklist everything this week because a single
    # very low time could be a legitimate accident
    if __check_event_single_threshold_breached(results, single_threshold):
        return __perform_single_results_blacklist_action(results, user), True

    # Everything's legit! Let those results through without blacklisting anything
    return __ensure_clean_unblacklisted(results), False

# -------------------------------------------------------------------------------------------------
# Functions and types below are not meant to be used directly; instead these are just dependencies
# of the publicly-visible functions above.
# -------------------------------------------------------------------------------------------------

def __ensure_clean_unblacklisted(results):
    """ Makes sure the blacklisted flag is explicitly false with an empty blacklisting note. """

    results.is_blacklisted = False
    results.blacklist_note = ''
    return results


def __perform_perma_blacklist_action(results, user):
    """ Blacklists this specific UserEventResults and sets the note indicating the user was flagged
    for permanent blacklist. """

    return __blacklist_results_with_note(results, __PERMA_BLACKLIST_NOTE_TEMPLATE)


def __perform_single_results_blacklist_action(results, user):
    """ Blacklists this specific UserEventResults and sets the note indicating the results were
    blacklisted due to being lower than the single threshold. """

    return __blacklist_results_with_note(results, __AUTO_BLACKLIST_NOTE_TEMPLATE, type=__SINGLE)


def __perform_average_results_blacklist_action(results, user):
    """ Blacklists this specific UserEventResults and sets the note indicating the results were
    blacklisted due to being lower than the single threshold. """

    # Blacklist these results and return
    return __blacklist_results_with_note(results, __AUTO_BLACKLIST_NOTE_TEMPLATE, type=__AVERAGE)


def __blacklist_results_with_note(results, note_template, **kwargs):
    """ Blacklists a UserEventResults and applies the provided blacklist note, which is assumed to be a
    template string. The keyword args provided to this function are formatted into the note as keyword args. """

    kwargs[__KEY_DATE] = now().format(__TIMESTAMP_FORMAT)
    results.is_blacklisted = True
    results.blacklist_note = note_template.format(**kwargs)

    return results


def __get_event_thresholds(comp_event_name):
    """ Retrieves the thresholds for single and average for the specified event, adjusted by an
    optional multiplicative factor from app config. """

    # Retrieve the WR thresholds tuple by event name
    event_thresholds = __AUTO_BLACKLIST_THRESHOLDS.get(comp_event_name, None)

    # If we don't have any thresholds for the event for some reason, then bail without taking action
    if not event_thresholds:
        return None

    # If this is for MBLD, just return the threshold itself directly.
    # It's a single value (points), not a tuple of (single, average) thresholds
    if comp_event_name == 'MBLD':
        return event_thresholds

    # A multiplicative factor to adjust autoblacklist thresholds up or down
    threshold_factor = app.config[__KEY_AUTO_BL_FACTOR]

    return (threshold_factor * entry for entry in event_thresholds)


def __check_event_single_threshold_breached(results, single_threshold):
    """ Checks if the results best single breaches the autoblacklist threshold for this event. """

    return __check_if_threshold_breached(results.single, single_threshold)


def __check_event_average_threshold_breached(results, average_threshold):
    """ Checks if the results average breaches the autoblacklist threshold for this event. """

    return __check_if_threshold_breached(results.average, average_threshold)


def __check_if_threshold_breached(results_value, threshold_value):
    """ Checks if the given results value breaches the supplied threshold. """

    # Return if the results value breaches the threshold
    try:
        return int(results_value) <= threshold_value

    # int() failed, it's probably a DNF
    except ValueError:
        return False
