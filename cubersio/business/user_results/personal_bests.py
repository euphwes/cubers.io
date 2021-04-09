""" Stuff related to handling user PBs (personal bests) in user event results. """

from cubersio.persistence.models import EventFormat
from cubersio.persistence.events_manager import get_event_format_for_event, get_events_name_id_mapping
from cubersio.persistence.user_results_manager import get_pb_single_event_results_except_current_comp,\
    bulk_save_event_results, get_pb_average_event_results_except_current_comp,\
    get_all_complete_user_results_for_user_and_event
from cubersio.util.events.resources import EVENT_MBLD

from cubersio.business.user_results import DNF

# -------------------------------------------------------------------------------------------------

EVENT_FORMATS_TO_SKIP_PB_AVERAGE_CHECK = [EventFormat.Bo1]

# -------------------------------------------------------------------------------------------------
# Functions and types below are intended to be used directly.
# -------------------------------------------------------------------------------------------------

def set_pb_flags(user_id, event_result, event_id, event_format):
    """ Sets the appropriate flag if either the single or average for this event is a PB. """

    pb_single, pb_average = __get_pbs_for_user_and_event_excluding_latest(user_id, event_id)

    # If the current single or average are tied with, or faster than, the user's current PB,
    # then flag this result as a PB. Tied PBs count as PBs in WCA rules
    if pb_single == __DNF_AS_PB and __pb_representation(event_result.single) == pb_single:
        event_result.was_pb_single = False  # Don't count DNFs beyond the first one as PBs
    else:
        event_result.was_pb_single = __pb_representation(event_result.single) <= pb_single

    # PB average flag isn't valid for Bo1, so don't bother checking
    # PB average flag isn't valid for MBLD, so don't bother checking
    if (event_format in EVENT_FORMATS_TO_SKIP_PB_AVERAGE_CHECK) or (event_id in [get_events_name_id_mapping()[EVENT_MBLD.name]]):
        event_result.was_pb_average = False
    else:
        if pb_average == __DNF_AS_PB and __pb_representation(event_result.average) == pb_average:
            event_result.was_pb_average = False  # Don't count DNFs beyond the first one as PBs
        else:
            event_result.was_pb_average = __pb_representation(event_result.average) <= pb_average

    return event_result


def recalculate_user_pbs_for_event(user_id, event_id):
    """ Recalculates PBs for all UserEventResults for the specified user and event. """

    # Get the user's event results for this event. If they don't have any, we can just bail
    results = get_all_complete_user_results_for_user_and_event(user_id, event_id)
    if not results:
        return

    event_format = get_event_format_for_event(event_id)

    # Start off at the beginning assuming no PBs
    pb_single_so_far  = __NO_PB_YET
    pb_average_so_far = __NO_PB_YET

    # Iterate over each result from earliest to latest, checking the singles and averages to see if they are faster than
    # the current fastest to date. Update the UserEventResult PB flags as appropriate.
    for result in results:

        result.is_latest_pb_single = False
        result.is_latest_pb_average = False

        # If the result is blacklisted, it's not under consideration for PBs.
        # Make sure the PB flags are False and skip to the next result.
        if result.is_blacklisted:
            result.was_pb_single  = False
            result.was_pb_average = False
            continue

        current_single  = __pb_representation(result.single)
        current_average = __pb_representation(result.average)

        # If the current single or average are tied with, or faster than, the user's current PB,
        # then flag this result as a PB. Tied PBs count as PBs in WCA rules.
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

    for result in reversed(results):
        if result.was_pb_single:
            result.is_latest_pb_single = True
            break

    for result in reversed(results):
        if result.was_pb_average:
            result.is_latest_pb_average = True
            break

    # Save all the UserEventResults with the modified PB flags
    bulk_save_event_results(results)

# -------------------------------------------------------------------------------------------------
# Functions and types below are not meant to be used directly; instead these are just dependencies
# of the publicly-visible functions above.
# -------------------------------------------------------------------------------------------------

# Integer representations of <DNF-as-a-PB> and <no PBs yet>.
# A DNF is a PB if no other PBs have been set, so <DNF-as-a-PB> is represented as a really slow time
# that's faster than <no PBs yet>.

# In centiseconds, this is ~28 years. Slower than any conceivable real time. Also this is "slower" by
# integer sorting than slower, low cube count MBLD results.
__PB_DNF    = 88888888888
__NO_PB_YET = 99999999999

def __pb_representation(time):
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


def __get_pbs_for_user_and_event_excluding_latest(user_id, event_id):
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
