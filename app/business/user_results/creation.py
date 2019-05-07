""" Methods related to creating UserEventResults. """

from sys import maxsize as MAX

from typing import Any, Dict, Iterable, Union, Tuple

from app.persistence.models import User, Nobody
from app.persistence.comp_manager import get_comp_event_by_id
from app.persistence.events_manager import get_event_by_name
from app.persistence.models import UserEventResults, UserSolve, EventFormat
from app.util.times import convert_centiseconds_to_friendly_time

from app.business.user_results.personal_bests import set_pb_flags

# -------------------------------------------------------------------------------------------------

# Keys to the dictionary passed from the front-end back to the server for creating UserEventResults
COMMENT       = 'comment'
SOLVES        = 'scrambles'  # Because the solve times are paired with the scrambles up front
TIME          = 'time'
SCRAMBLE_ID   = 'id'
IS_DNF        = 'isDNF'
IS_PLUS_TWO   = 'isPlusTwo'
COMP_EVENT_ID = 'comp_event_id'
NAME          = 'name'

# Other useful constant values
FMC          = 'FMC'
DNF          = 'DNF'
BLIND_EVENTS = ('2BLD', '3BLD', '4BLD', '5BLD')

# -------------------------------------------------------------------------------------------------
# Functions and types below are intended to be used directly.
# -------------------------------------------------------------------------------------------------

def build_user_event_results(comp_event_id: int,
                             comp_event_dict: Dict[str, Any],
                             user: Union[User, Nobody]) -> Tuple[UserEventResults, str]:
    """ Builds a UserEventsResult object from a dictionary coming in from the front-end, which
    contains the competition event ID and the user's solves paired with the scrambles. """

    comment = comp_event_dict.get(COMMENT, '')

    # Retrieve the CompetitionEvent from the DB and get the event name, format, and expected solves
    comp_event          = get_comp_event_by_id(comp_event_id)
    event_id            = comp_event.Event.id
    event_name          = comp_event.Event.name
    event_format        = comp_event.Event.eventFormat
    expected_num_solves = comp_event.Event.totalSolves

    # Create the actual UserEventResults
    results = UserEventResults(comp_event_id=comp_event_id, comment=comment)

    # Build up a list of UserSolves for this UserEventResults
    solves = __build_user_solves(comp_event_dict[SOLVES], is_fmc=event_name == FMC)
    results.set_solves(solves)

    # Set the best single and overall average for this event
    __set_single_and_average(results, expected_num_solves, event_format)

    # Determine if the user has completed their results for this event
    __set_is_complete(results, event_format, expected_num_solves)

    # Figure out if this is for FMC, a blind event, or neither
    # Useful for deciding how to represent results to the user
    results.is_fmc   = event_name == FMC
    results.is_blind = event_name in BLIND_EVENTS

    # If the results are not yet complete, go ahead and return now
    if not results.is_complete:
        return results, event_name

    # Set the result (either best single, mean, or average) depending on event format
    results.result = __determine_event_result(results.single, results.average, event_format)

    # Store the "times string" so we don't have to recalculate this again later.
    # It's fairly expensive, so doing this for every UserEventResults in the competition slows
    # down the leaderboards noticeably.
    results.times_string = __build_times_string(results, event_format)

    # Determine and set if the user set any PBs in this event.
    # If there's no user, no need to check PB flags.
    if user:
        set_pb_flags(user, results, event_id, event_format)

    return results, event_name

# -------------------------------------------------------------------------------------------------
# Functions and types below are not meant to be used directly; instead these are just dependencies
# of the publicly-visible functions above.
# -------------------------------------------------------------------------------------------------

def __build_user_solves(solves_data, is_fmc=False) -> Iterable[UserSolve]:
    """ Builds and returns a list of UserSolves from the data coming from the front end. """

    user_solves = list()

    for solve in solves_data:
        time = solve[TIME]

        # If the user hasn't recorded a time for this scramble, then just skip to the next
        # For FMC, no-time-but-DNF is allowed
        if not time and not (is_fmc and solve[IS_DNF]):
            continue

        # Set the time (in centiseconds), DNF and +2 status, and the scramble ID for this UserSolve
        time        = int(time)
        dnf         = solve[IS_DNF]
        plus_two    = solve[IS_PLUS_TWO]
        scramble_id = solve[SCRAMBLE_ID]

        user_solve = UserSolve(time=time, is_dnf=dnf, is_plus_two=plus_two, scramble_id=scramble_id)
        user_solves.append(user_solve)

    return user_solves


def __set_is_complete(user_event_results, event_format, expected_num_solves):
    """ Determine whether this event is considered complete or not. """

    # All blind events are best-of-3, but ranked by single,
    # so consider those complete if there are any solves complete at all
    if event_format == EventFormat.Bo3:
        user_event_results.is_complete = bool(user_event_results.solves)

    # Other events are complete if all solves have been completed
    else:
        user_event_results.is_complete = len(user_event_results.solves) == expected_num_solves


def __set_single_and_average(user_event_results, expected_num_solves, event_format):
    """ Determines and sets the best single and average for the UserEventResults. """

    # If not all the solves have been completed, we only know the single
    if len(user_event_results.solves) < expected_num_solves:
        user_event_results.single  = __determine_best_single(user_event_results.solves)
        user_event_results.average = ''

    # Otherwise set the single and average if all solves are done
    else:
        single, average = __determine_bests(user_event_results.solves, event_format)
        user_event_results.single  = single
        user_event_results.average = average


def __build_event_summary(event, user):
    """ Builds the times summary for the event and returns it.
    Ex. 2:49.46 = 2:53.39, 2:44.87, (2:58.07), 2:50.14, (2:26.52) """

    event_name   = event[NAME]
    event_format = get_event_by_name(event_name).eventFormat

    # Wrap up the events data in the format expected by `build_user_event_results`
    event_data_dict = dict()
    event_data_dict[event[COMP_EVENT_ID]] = event

    # Build up the UserEventResults
    results, _ = build_user_event_results(event_data_dict, user)

    # If the format is Bo1 (best of 1) just return human-friendly representation of the time
    if event_format == EventFormat.Bo1:
        return convert_centiseconds_to_friendly_time(results.single)

    # The time on the left side of the `=` is the best single in a Bo3 event, otherwise it's the
    # overall average for the event
    best = results.single if (event_format == EventFormat.Bo3) else results.average

    # If this isn't FMC, convert to human-friendly time
    if not event_name == FMC:
        best = convert_centiseconds_to_friendly_time(best)

    # If this is FMC, convert the faux centiseconds representation to the number of moves
    # 2833 --> 28.33 moves
    # If the number of moves is an integer, represent it without the trailing ".00"
    # 2800 --> 28 moves, not 28.00 moves
    else:
        best = best / 100
        if best == int(best):
            best = int(best)

    return "{} = {}".format(best, results.times_string)


def __build_times_string(results, event_format, want_list=False):
    """ Builds a list of individual times, with best/worst times in parens if appropriate
    for the given event format. """

    # TODO: comment this more thorougly below

    solves = results.solves

    time_convert = convert_centiseconds_to_friendly_time

    # Bo1 is special, just return the friendly representation of the one time
    if event_format == EventFormat.Bo1:
        return 'DNF' if solves[0].is_dnf else time_convert(solves[0].get_total_time())

    # FMC is special, the 'time' is actually the number of moves, not number of centiseconds
    # so don't convert to "friendly times" because that makes no sense
    if not results.is_fmc:
        friendly_times = [time_convert(solve.get_total_time()) for solve in solves]
    else:
        friendly_times = [str(int(solve.get_total_time() / 100)) for solve in solves]

    for i, solve in enumerate(solves):
        if solve.is_plus_two:
            friendly_times[i] = friendly_times[i] + "+"

    curr_best   = MAX
    curr_worst  = -1
    best_index  = -1
    worst_index = -1

    dnf_indicies   = list()
    have_found_dnf = False

    for i, solve in enumerate(solves):
        if (not solve.is_dnf) and (solve.get_total_time() < curr_best):
            best_index = i
            curr_best  = solve.get_total_time()

        if (not have_found_dnf) and (solve.get_total_time() > curr_worst):
            worst_index = i
            curr_worst  = solve.get_total_time()

        if solve.is_dnf:
            if not have_found_dnf:
                worst_index = i
                have_found_dnf = True
            dnf_indicies.append(i)

    for i in dnf_indicies:
        if results.is_blind:
            friendly_times[i] = 'DNF(' + friendly_times[i] + ')'
        else:
            friendly_times[i] = 'DNF'

    if event_format == EventFormat.Bo3:
        while len(friendly_times) < 3:
            friendly_times.append('DNS')

    if event_format in [EventFormat.Bo3, EventFormat.Mo3]:
        return friendly_times if want_list else ', '.join(friendly_times)

    friendly_times[best_index] = '({})'.format(friendly_times[best_index])
    friendly_times[worst_index] = '({})'.format(friendly_times[worst_index])

    return friendly_times if want_list else ', '.join(friendly_times)

# -------------------------------------------------------------------------------------------------
#    Logic for determining best single and average from a set of solves, for a given EventFormat
# -------------------------------------------------------------------------------------------------

def __determine_best_single(solves):
    """ Determines the best single in the set of solves. """

    # If all solves are DNF, then DNF is the best we've got
    if all(solve.is_dnf for solve in solves):
        return DNF

    # Otherwise if we have a non-DNF time, return the minimum total time (including penalties)
    # across all non-DNF solves
    return min(solve.get_total_time() for solve in solves if not solve.is_dnf)


def __determine_event_result(single: Union[str, int],
                             average: Union[str, int],
                             event_format: EventFormat) -> Union[str, int]:
    """ Returns the correct overall result (either single or average) based on the event format. """

    results_dict = {
        EventFormat.Ao5: average,
        EventFormat.Mo3: average,
        EventFormat.Bo3: single,
        EventFormat.Bo1: single,
    }

    try:
        return results_dict[event_format]
    except KeyError:
        raise ValueError(event_format, '{event_format} is not a valid event format.')


def __determine_bests(solves, event_format):
    """ Returns a tuple of (best single, average) for these solves based on the supplied
    event format." """

    bests_func_dict = {
        EventFormat.Ao5: __determine_bests_ao5,
        EventFormat.Mo3: __determine_bests_mo3,
        EventFormat.Bo3: __determine_bests_bo3,
        EventFormat.Bo1: __determine_bests_bo1,
    }

    try:
        return bests_func_dict[event_format](solves)
    except KeyError:
        raise ValueError(event_format, '{event_format} is not a valid event format.')


def __determine_bests_bo1(solves):
    """ Returns just the one single. """

    solve = solves[0]

    if solve.is_dnf:
        return DNF, ''

    return solve.get_total_time(), ''


def __determine_bests_bo3(solves):
    """ Returns the best single for these 3 solves, and 'N/A' for the average. """
    return __determine_bests_mo3(solves)


def __determine_bests_mo3(solves):
    """ Returns the best single and mean for these 3 solves. """

    dnf_count = sum(1 for solve in solves if solve.is_dnf)

    if dnf_count > 0:
        average = DNF
    else:
        average = round(sum(solve.get_total_time() for solve in solves) / 3.0)

    if dnf_count == 3:
        single = DNF
    else:
        single = min(solve.get_total_time() for solve in solves if not solve.is_dnf)

    return single, average


def __determine_bests_ao5(solves):
    """ Returns the best single and average for these 5 solves, where the average
    is the arithmetic mean of the middle 3 solves. """

    dnf_count = sum(1 for solve in solves if solve.is_dnf)

    if dnf_count == 0:
        times   = [solve.get_total_time() for solve in solves]
        best    = min(times)
        worst   = max(times)
        average = round((sum(times) - best - worst) / 3.0)

    elif dnf_count == 1:
        times   = [solve.get_total_time() for solve in solves if not solve.is_dnf]
        best    = min(times)
        average = round((sum(times) - best) / 3.0)

    elif dnf_count == 5:
        average = DNF
        best    = DNF

    else:
        times   = [solve.get_total_time() for solve in solves if not solve.is_dnf]
        average = DNF
        best    = min(times)

    return best, average
