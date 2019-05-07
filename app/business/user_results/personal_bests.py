""" Stuff related to handling user PBs (personal bests) in user event results. """

from typing import Union, Tuple

from app.persistence.models import EventFormat, UserEventResults
from app.persistence.events_manager import get_event_format_for_event
from app.persistence.user_results_manager import get_pb_single_event_results_except_current_comp,\
    bulk_save_event_results, get_pb_average_event_results_except_current_comp,\
    get_all_complete_user_results_for_user_and_event

from app.business.user_results import DNF

# -------------------------------------------------------------------------------------------------
# Functions and types below are intended to be used directly.
# -------------------------------------------------------------------------------------------------

def set_pb_flags(event_result: UserEventResults,
                 event_id: int,
                 event_format: EventFormat) -> UserEventResults:
    """ Sets the appropriate flag if either the single or average for this event is a PB. """

    pb_single, pb_average = __get_pbs_for_user_and_event_excluding_latest(event_result.user_id, event_id)

    # If the current single or average are tied with, or faster than, the user's current PB,
    # then flag this result as a PB. Tied PBs count as PBs in WCA rules
    if pb_single == __DNF_AS_PB and __pb_representation(event_result.single) == pb_single:
        event_result.was_pb_single = False  # Don't count DNFs beyond the first one as PBs
    else:
        event_result.was_pb_single = __pb_representation(event_result.single) <= pb_single

    # PB average flag for Bo1 isn't valid, so don't bother checking
    if event_format != EventFormat.Bo1:
        if pb_average == __DNF_AS_PB and __pb_representation(event_result.average) == pb_average:
            event_result.was_pb_average = False  # Don't count DNFs beyond the first one as PBs
        else:
            event_result.was_pb_average = __pb_representation(event_result.average) <= pb_average
    else:
        event_result.was_pb_average = False

    return event_result


def recalculate_user_pbs_for_event(user_id: int, event_id: int) -> None:
    """ Recalculates PBs for all UserEventResults for the specified user and event. """

    # Get the user's event results for this event. If they don't have any, we can just bail
    results = get_all_complete_user_results_for_user_and_event(user_id, event_id)
    if not results:
        return

    event_format = get_event_format_for_event(event_id)

    # Store the results to save all at once at the end
    event_results_to_save_at_end = list()
    event_results_to_save_at_end.extend(results)

    # Start off at the beginning assuming no PBs
    pb_single_so_far  = __NO_PB_YET
    pb_average_so_far = __NO_PB_YET

    # Iterate over each result from earliest to latest, checking the singles and averages to see
    # if they are faster than the current fastest to date. Update the UserEventResult PB flags
    # as appropriate
    for result in results:

        # If the result is blacklisted, it's not under consideration for PBs.
        # Make sure the PB flags are False and skip to the next result
        if result.is_blacklisted:
            result.was_pb_single  = False
            result.was_pb_average = False
            continue

        current_single  = __pb_representation(result.single)
        current_average = __pb_representation(result.average)

        # If the current single or average are tied with, or faster than, the user's current PB,
        # then flag this result as a PB. Tied PBs count as PBs in WCA rules
        if __DNF_AS_PB == pb_single_so_far and __DNF_AS_PB == current_single:
            result.was_pb_single = False
        elif current_single <= pb_single_so_far:
            pb_single_so_far = current_single
            result.was_pb_single = True
        else:
            result.was_pb_single = False

        # PB average flag for Bo1 isn't valid, so don't bother checking
        if event_format != EventFormat.Bo1:
            if __DNF_AS_PB == pb_average_so_far and __DNF_AS_PB == current_average:
                result.was_pb_average = False
            elif current_average <= pb_average_so_far:
                pb_average_so_far = current_average
                result.was_pb_average = True
            else:
                result.was_pb_average = False
        else:
            result.was_pb_average = False

    # Save all the UserEventResults with the modified PB flags
    bulk_save_event_results(event_results_to_save_at_end)

# -------------------------------------------------------------------------------------------------
# Functions and types below are not meant to be used directly; instead these are just dependencies
# of the publicly-visible functions above.
# -------------------------------------------------------------------------------------------------

# Integer representations of <DNF-as-a-PB> and <no PBs yet>.
# A DNF is a PB if no other PBs have been set, so <DNF-as-a-PB> is represented as a really slow time
# that's faster than <no PBs yet>.

__PB_DNF    = 88888888  # In centiseconds, this is ~246 hours. Slower than any conceivable real time
__NO_PB_YET = 99999999

def __pb_representation(time: Union[int, str]) -> int:
    """ Takes a `time` value from a user solve and converts it into a representation useful for
    determining PBs. Strings or lack of times are represented as integers, and numbers are returned
    directly as integers for direct comparison. """

    if time == DNF:
        return __PB_DNF
    elif time == '':
        return __NO_PB_YET
    else:
        return int(time)

__DNF_AS_PB = __pb_representation(DNF)


def __get_pbs_for_user_and_event_excluding_latest(user_id: int,
                                                  event_id: int) -> Tuple[int, int]:
    """ Returns a tuple of PB single and average for this event for the specified user, except
    for the current comp. Excluding the current comp allows for the user to keep updating their
    results for this comp, and the logic determining if this comp has a PB result doesn't include
    this comp itself. """

    results_with_pb_singles = get_pb_single_event_results_except_current_comp(user_id, event_id)
    singles = [__pb_representation(r.single) for r in results_with_pb_singles]
    pb_single = min(singles) if singles else __NO_PB_YET

    results_with_pb_averages = get_pb_average_event_results_except_current_comp(user_id, event_id)
    averages = [__pb_representation(r.average) for r in results_with_pb_averages]
    pb_average = min(averages) if averages else __NO_PB_YET

    return pb_single, pb_average
