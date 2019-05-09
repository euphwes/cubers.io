
from typing import Tuple, Union

from arrow import now

from app import app
from app.persistence.models import UserEventResults, User
from app.persistence.comp_manager import get_comp_event_name_by_id

# -------------------------------------------------------------------------------------------------

__TIMESTAMP_FORMAT = 'YYYY-MM-DD'

# Threshold breached blacklist note
__AUTO_BLACKLIST_NOTE_TEMPLATE = "Results automatically hidden on {date} because the user's {type} is "
__AUTO_BLACKLIST_NOTE_TEMPLATE += "less than the threshold for this event."

# Permanent blacklist note
__PERMA_BLACKLIST_NOTE_TEMPLATE = "Results automatically hidden on {date} because this user is flagged for "
__PERMA_BLACKLIST_NOTE_TEMPLATE += "permanent blacklist."

# For retrieving blacklist threshold multiplicative factor from app config
__KEY_AUTO_BL_FACTOR = 'AUTO_BL_FACTOR'

# Values to be inserted into blacklist note templates above, and key for a kwargs dict
# to insert timestamp as `date` kwarg
__SINGLE   = 'single'
__AVERAGE  = 'average'
__KEY_DATE = 'date'

# Dictionary of event name to tuple of (WR single, WR average) in centiseconds
# WCA WRs as of 12 Apr 2019
__AUTO_BLACKLIST_THRESHOLDS = {
    '2x2':           (49, 121),
    '3x3':           (347, 580),
    '4x4':           (1842, 2113),
    '5x5':           (3728, 4236),
    '6x6':           (7382, 7710),
    '7x7':           (10789, 11163),
    '3BLD':          (1655, 2012),
    '4BLD':          (8641, 1),   # very low dummy average because WCA doesn't track 4BLD WR average
    '5BLD':          (16942, 1),  # very low dummy average because WCA doesn't track 5BLD WR average
    'Square-1':      (500, 673),
    'Clock':         (340, 456),
    '3x3OH':         (688, 942),
    'Pyraminx':      (91, 187),
    'Megaminx':      (2781, 3203),
    'Skewb':         (110, 203),
    'FMC':           (1700, 2400),  # in "centi-moves"
    '3x3 With Feet': (1696, 2222),

    # Below are thresholds for "reasonable" times for bonus events, based on times that have been
    # submitted for bonus events over the last few months. Mostly gave a few seconds of buffer underneath
    # what the current site records are for these events.
    'Kilominx':        (1400, 1600),
    '2BLD':            (350, 450),
    'Redi Cube':       (400, 600),
    'Void Cube':       (500, 700),
    '4x4 OH':          (4500, 5000),
    '3x3x2':           (250, 400),
    '3x3x4':           (2200, 2800),
    '3x3x5':           (3500, 4000),
    '2GEN':            (150, 250),
    'F2L':             (175, 275),
    '2-3-4 Relay':     (3200, 1),
    '3x3 Relay of 3':  (2000, 1),
    'PLL Time Attack': (2200, 1),
    '3x3 Mirror Blocks/Bump': (2000, 2500),

    # "Reasonable values" sourced from
    # https://www.speedsolving.com/wiki/index.php/List_of_Unofficial_World_Records
    # and then rounded down another 15s or so just in case
    '8x8': (21000, 1),
    '9x9': (31500, 1),
}

# -------------------------------------------------------------------------------------------------
# Functions and types below are intended to be used directly.
# -------------------------------------------------------------------------------------------------

def take_blacklist_action_if_necessary(results: UserEventResults,
                                       user: User) -> Tuple[UserEventResults, bool]:
    """ Determines if this UserEventResults should be auto-blacklisted because of an absurdly low
    time. Uses a multiplicative factor of the current world records as a threshold, which is
    adjustable by environment variable. """

    # If the results aren't complete, return early since we don't need to blacklist yet
    if not results.is_complete:
        app.logger.info('not blacklisting, incomplete')
        return results, False

    # Check if the user is flagged to have all of their results automatically blacklisted
    if user.always_blacklist:
        return __perform_perma_blacklist_action(results), True

    # TODO: weekly blacklist

    # Get the auto-blacklist thresholds for the event these results are for.
    # If we don't have thresholds, leave without taking any blacklist action
    comp_event_name = get_comp_event_name_by_id(results.comp_event_id)
    thresholds      = __get_event_thresholds(comp_event_name)
    if not thresholds:
        return results, False

    # Extract the adjusted single and average thresholds
    single_threshold, average_threshold = thresholds

    # If the single threshold has been breached, blacklist just the one set of results.
    # We don't want to go overboard and blacklist everything this week because a single
    # very low time could be a legitimate accident
    if __check_event_single_threshold_breached(results, single_threshold):
        return __perform_single_results_autoblacklist_action(results, comp_event_name), True

    # If the average threshold has been breached, it's more likely that the user is
    # intentionally posting bogus times. Blacklist this set of results, add a
    # WeeklyBlacklist record to indicate that other results posted this week are to be
    # automatically blacklisted, and fire off a task to retroactively blacklist other results
    # already posted this week.
    if __check_event_average_threshold_breached(results, average_threshold):
        return __perform_average_results_autoblacklist_action(results, comp_event_name), True

    # Everything's legit! Let those results through without blacklisting anything
    return results, False

# -------------------------------------------------------------------------------------------------
# Functions and types below are not meant to be used directly; instead these are just dependencies
# of the publicly-visible functions above.
# -------------------------------------------------------------------------------------------------

def __perform_perma_blacklist_action(results: UserEventResults) -> UserEventResults:
    """ Blacklists this specific UserEventResults and sets the note indicating the user was flagged
    for permanent blacklist. """

    return __blacklist_results_with_note(results, __PERMA_BLACKLIST_NOTE_TEMPLATE)


def __perform_single_results_autoblacklist_action(results: UserEventResults,
                                                  comp_event_name: str) -> UserEventResults:
    """ Blacklists this specific UserEventResults and sets the note indicating the results were
    blacklisted due to being lower than the single threshold. """

    return __blacklist_results_with_note(results, __AUTO_BLACKLIST_NOTE_TEMPLATE, type=__SINGLE)


def __perform_average_results_autoblacklist_action(results: UserEventResults,
                                                   comp_event_name: str) -> UserEventResults:
    """ Blacklists this specific UserEventResults and sets the note indicating the results were
    blacklisted due to being lower than the single threshold. """

    # TODO set weekly blacklist flag
    # TODO kick off task to blacklist result of results this week
    return __blacklist_results_with_note(results, __AUTO_BLACKLIST_NOTE_TEMPLATE, type=__AVERAGE)


def __blacklist_results_with_note(results: UserEventResults,
                                  note_template: str,
                                  **kwargs) -> UserEventResults:
    """ Blacklists a UserEventResults and applies the provided blacklist note, which is assumed to be a
    template string. The keyword args provided to this function are formatted into the note as keyword args. """

    kwargs[__KEY_DATE] = now().format(__TIMESTAMP_FORMAT)
    results.is_blacklisted = True
    results.blacklist_note = note_template.format(**kwargs)

    return results


def __get_event_thresholds(comp_event_name: str) -> Union[Tuple[float, float], None]:
    """ Retrieves the thresholds for single and average for the specified event, adjusted by an
    optional multiplicative factor from app config. """

    # Retrieve the WR thresholds tuple by event name
    event_thresholds = __AUTO_BLACKLIST_THRESHOLDS.get(comp_event_name, None)

    # If we don't have any thresholds for the event for some reason, then bail without taking action
    if not event_thresholds:
        return None

    # A multiplicative factor to adjust autoblacklist thresholds up or down
    threshold_factor = app.config[__KEY_AUTO_BL_FACTOR]

    return (threshold_factor * entry for entry in event_thresholds)


def __check_event_single_threshold_breached(results: UserEventResults,
                                            single_threshold: float) -> bool:
    """ Checks if the results best single breaches the autoblacklist threshold for this event. """

    return __check_if_threshold_breached(results.single, single_threshold)


def __check_event_average_threshold_breached(results: UserEventResults,
                                             average_threshold: float) -> bool:
    """ Checks if the results average breaches the autoblacklist threshold for this event. """

    return __check_if_threshold_breached(results.average, average_threshold)


def __check_if_threshold_breached(results_value: str,
                                  threshold_value: float) -> bool:
    """ Checks if the given results value breaches the supplied threshold. """

    # Return if the results value breaches the threshold
    try:
        return int(results_value) <= threshold_value

    # int() failed, it's probably a DNF
    except ValueError:
        return False
