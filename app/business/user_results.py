
from sys import maxsize as MAX

from typing import Dict, List

from arrow import now

from app import app
from app.persistence.comp_manager import get_comp_event_by_id
from app.persistence.events_manager import get_event_by_name, get_event_format_for_event
from app.persistence.user_results_manager import get_pb_single_event_results_except_current_comp,\
    bulk_save_event_results, get_pb_average_event_results_except_current_comp,\
    get_all_complete_user_results_for_user_and_event, get_results_for_comp_event
from app.persistence.models import UserEventResults, UserSolve, EventFormat
from app.util.sorting import sort_user_event_results
from app.util.times import convert_centiseconds_to_friendly_time
from app.util.events.resources import get_non_WCA_event_names


# Auto-blacklist notes
_AUTO_BLACKLIST_NOTE_TEMPLATE = "Results automatically hidden on {date} because the {type} is less than the "
_AUTO_BLACKLIST_NOTE_TEMPLATE += "'{factor} * WR {type}' threshold for this event."

# Bonus event blacklist notes
_AUTO_BONUS_BL_NOTE_TEMPLATE = "Results automatically hidden on {date} because the {type} is less than the "
_AUTO_BONUS_BL_NOTE_TEMPLATE += "{type} 'reasonable' threshold for this event."

SINGLE  = 'single'
AVERAGE = 'average'

def determine_if_should_be_autoblacklisted(results):
    """ Determines if this UserEventResults should be auto-blacklisted because of an absurdly low
    time. Uses a multiplicative factor of the current world records as a threshold, which is
    adjustable by environment variable. """

    # If the results aren't complete, don't blacklist yet even if we otherwise would have
    if not results.is_complete:
        return results

    # A multiplicative factor to adjust autoblacklist thresholds up or down, relative to WR
    threshold_factor = app.config['AUTO_BL_FACTOR']

    # Dictionary of event name to tuple of (WR single, WR average) in centiseconds
    # WCA WRs as of 12 Apr 2019
    # pylint: disable=C0301
    blacklist_thresholds = {
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

    # Retrieve the WR thresholds tuple by event name
    comp_event = get_comp_event_by_id(results.comp_event_id)
    thresholds = blacklist_thresholds.get(comp_event.Event.name, None)

    # If we don't have any thresholds for the event, no chance of auto-blacklist
    if not thresholds:
        return results

    wr_single, wr_average = thresholds

    # Check if the result's single should cause this to be auto-blacklisted
    try:
        # If the single is too low, set the blacklisted flag and note,
        # and unset any PB flags which were probably set earlier when
        # build the UserEventResults
        if int(results.single) <= (threshold_factor * wr_single):
            timestamp = now().format('YYYY-MM-DD')
            if comp_event.Event.name in get_non_WCA_event_names():
                note = _AUTO_BONUS_BL_NOTE_TEMPLATE.format(type=SINGLE, date=timestamp)
            else:
                note = _AUTO_BLACKLIST_NOTE_TEMPLATE.format(type=SINGLE, date=timestamp, factor=threshold_factor)
            results.blacklist_note = note
            results.is_blacklisted = True
            results.was_pb_average = False
            results.was_pb_single  = False
            return results
    except ValueError:
        pass  # int() failed, probably because the single is a DNF

    # Check if the result's average should cause this to be auto-blacklisted
    try:
        # If the average is too low, set the blacklisted flag and note,
        # and unset any PB flags which were probably set earlier when
        # build the UserEventResults
        if int(results.average) <= (threshold_factor * wr_average):
            timestamp = now().format('YYYY-MM-DD')
            if comp_event.Event.name in get_non_WCA_event_names():
                note = _AUTO_BONUS_BL_NOTE_TEMPLATE.format(type=SINGLE, date=timestamp)
            else:
                note = _AUTO_BLACKLIST_NOTE_TEMPLATE.format(type=SINGLE, date=timestamp, factor=threshold_factor)
            results.blacklist_note = note
            results.is_blacklisted = True
            results.was_pb_average = False
            results.was_pb_single  = False
            return results
    except ValueError:
        pass # int() failed, probably because the average is a DNF

    return results

# -------------------------------------------------------------------------------------------------
#              Stuff related to processing medals for top results in events
# -------------------------------------------------------------------------------------------------

def set_medals_on_best_event_results(comp_events):
    """ Iterates over a list of CompetitionEvents, gets the fastest 3 results for that event and
    sets the gold, silver, or bronze medal flags as appropriate. """

    for comp_event in comp_events:
        results = get_results_for_comp_event(comp_event.id)

        # Simultaneously pull out the unblacklisted results, and ensure that blacklisted
        # results do not have any medals set.
        unblacklisted_results = list()
        for result in results:
            if result.is_blacklisted:
                result.was_bronze_medal = False
                result.was_silver_medal = False
                result.was_gold_medal   = False
            else:
                unblacklisted_results.append(result)

        # Sort the unblacklisted results by their result value
        unblacklisted_results.sort(key=sort_user_event_results)

        # 1st is gold medal, 2nd is silver, 3rd is bronze, everything else has no medal
        for i, result in enumerate(unblacklisted_results):
            result.was_gold_medal   = (i == 0) and result.result != 'DNF'
            result.was_silver_medal = (i == 1) and result.result != 'DNF'
            result.was_bronze_medal = (i == 2) and result.result != 'DNF'

        # Save all event results with their updated medal flags
        bulk_save_event_results(results)

