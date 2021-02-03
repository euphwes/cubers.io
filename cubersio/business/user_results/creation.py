""" Methods related to creating UserEventResults. """

from sys import maxsize as MAX

from cubersio.persistence.models import EventFormat
from cubersio.util.events import build_mbld_results
from cubersio.util.times import convert_centiseconds_to_friendly_time
from cubersio.business.user_results import DNF, DNS
from cubersio.business.user_results.personal_bests import set_pb_flags
from cubersio.business.user_results.blacklisting import take_blacklist_action_if_necessary
from cubersio.util.events.resources import EVENT_FMC, EVENT_MBLD, EVENT_2BLD, EVENT_3BLD, EVENT_4BLD, EVENT_5BLD

# -------------------------------------------------------------------------------------------------

# Summary and times strings templates
EVENT_SUMMARY_TEMPLATE         = '{result} = {times_string}'
PLUS_TWO_SOLVE_TEMPLATE        = '{solve_time}+'
BLIND_EVENT_DNF_SOLVE_TEMPLATE = 'DNF({solve_time})'
SOLVE_PARENS_TEMPLATE          = '({solve_time})'
SOLVE_TIMES_SEPARATOR          = ', '

# -------------------------------------------------------------------------------------------------
# Functions and types below are intended to be used directly.
# -------------------------------------------------------------------------------------------------

def process_event_results(results, comp_event, user):
    """ Processes a UserEventsResult object to determine best single, averages, is_complete flag, etc. """

    event_id            = comp_event.Event.id
    event_format        = comp_event.Event.eventFormat
    expected_num_solves = comp_event.Event.totalSolves
    event_name          = comp_event.Event.name

    # Set the best single and overall average for this event
    __set_single_and_average(results, expected_num_solves, event_format)

    # Determine if the user has completed their results for this event
    __set_is_complete(results, event_format, expected_num_solves)

    # If the results are not yet complete, go ahead and return now.
    if not results.is_complete:
        return results

    # A couple of "is_<thisThing>" flags to facilitate some one-off logic
    is_fmc = event_name == EVENT_FMC.name
    is_mbld = event_name == EVENT_MBLD.name
    is_blind = event_name in (EVENT_2BLD.name, EVENT_3BLD.name, EVENT_4BLD.name, EVENT_5BLD.name)

    # Specifically MBLD doesn't have means, even though other Bo3 events do
    if is_mbld:
        results.average = ''

    # Set the result (either best single, mean, or average) depending on event format
    results.result = __determine_event_result(results.single, results.average, event_format)

    # Store the "times string" so we don't have to recalculate this again later.
    # It's fairly expensive, so doing this for every UserEventResults in the competition slows
    # down the leaderboards noticeably.
    results.times_string = __build_times_string(results, event_format, is_fmc, is_blind, is_mbld)

    # Determine if these results need to be automatically blacklisted because either they have
    # suspect times, or if some other criteria is causing them to be blacklisted, and set the
    # blacklisting flag as necessary.
    results, was_blacklisting_action_taken = take_blacklist_action_if_necessary(results, user)

    # If these results were not blacklisted, determine if the user set any PBs in this event
    if not was_blacklisting_action_taken:
        results = set_pb_flags(user.id, results, event_id, event_format)

    return results

# -------------------------------------------------------------------------------------------------
# Functions and types below are not meant to be used directly; instead these are just dependencies
# of the publicly-visible functions above.
# -------------------------------------------------------------------------------------------------

def __set_is_complete(user_event_results, event_format, expected_num_solves):
    """ Determine whether this event is considered complete or not. """

    # All blind events are best-of-3, but ranked by single, so consider those complete if there
    # are any solves complete at all
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

    # Otherwise set the single and average
    else:
        single, average = __determine_bests(user_event_results.solves, event_format)
        user_event_results.single  = single
        user_event_results.average = average


def __build_times_string(results, event_format, is_fmc, is_blind, is_mbld):
    """ Builds a list of individual times, with best and worst times in parentheses if appropriate
    for the given event format. """

    # Extract the solves out of the UserEventResults, since we'll be using them often
    solves = results.solves

    # Bo1 is special, just return the friendly representation of the one time
    if event_format == EventFormat.Bo1:
        first_solve = solves[0]
        if first_solve.is_dnf:
            return DNF
        else:
            if is_mbld:
                return build_mbld_results(first_solve.get_total_time())
            else:
                return convert_centiseconds_to_friendly_time(first_solve.get_total_time())

    # Build a list which contains the user-friendly representation of the total solve time for each solve
    if not is_fmc:
        if is_mbld:
            friendly_times = [build_mbld_results(solve.get_total_time()) for solve in solves]
        else:
            friendly_times = [convert_centiseconds_to_friendly_time(solve.get_total_time()) for solve in solves]

    # FMC is special, the 'time' is actually the number of moves, not number of centiseconds, so instead
    # interpret the time value here as "centimoves" and convert to integer number of moves represented as a string
    else:
        friendly_times = [str(int(solve.get_total_time() / 100)) for solve in solves]

    # Iterate over the solves themselves, and if any of those solves have +2 penalty, add a '+' marker to the
    # corresponding user-friendly representation of that time
    for i, solve in enumerate(solves):
        if solve.is_plus_two:
            friendly_times[i] = PLUS_TWO_SOLVE_TEMPLATE.format(solve_time=friendly_times[i])

    # Initialize some variables to hold the current best and worst times, and the index at which they
    # reside, so we mark those with parentheses
    curr_best   = MAX
    curr_worst  = -1
    best_index  = -1
    worst_index = -1

    # Store the indices of any DNFs, so we can denote replace the user-friendly times with "DNF"
    dnf_indicies   = list()
    have_found_dnf = False

    # Iterate over each list, and check if the solve is the current best or worst time, remembering the
    # index if it is. Only the first DNF counts as the worst time. Remember indices of each DNF
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

    # For all DNFs in the solve, replace the corresponding user-friendly time with "DNF",
    # or wrap the time with "DNF(<time>)" for blind events
    for i in dnf_indicies:
        if is_blind:
            friendly_times[i] = BLIND_EVENT_DNF_SOLVE_TEMPLATE.format(solve_time=friendly_times[i])
        else:
            friendly_times[i] = DNF

    # Best-of-3 events can be "complete" without all solves being finished.
    # If we have fewer than 3 times for a Bo3 event, keep adding 'DNS' (did not start) until
    # we have 3 time entries
    if event_format == EventFormat.Bo3:
        while len(friendly_times) < 3:
            friendly_times.append(DNS)

    # For Bo3 and Mo3 event formats, we don't enclose best and worst times in parentheses.
    # Return the list of times if a list is requested, otherwise join each time with a comma and
    # return the final result.
    if event_format in [EventFormat.Bo3, EventFormat.Mo3]:
        return SOLVE_TIMES_SEPARATOR.join(friendly_times)

    # For other event formats, we enclose the best and worst times in parentheses.
    friendly_times[best_index]  = SOLVE_PARENS_TEMPLATE.format(solve_time=friendly_times[best_index])
    friendly_times[worst_index] = SOLVE_PARENS_TEMPLATE.format(solve_time=friendly_times[worst_index])

    # Return the list of times if a list is requested, otherwise join each time with a comma and
    # return the final result.
    return SOLVE_TIMES_SEPARATOR.join(friendly_times)

# -------------------------------------------------------------------------------------------------
#    Logic for determining best single and average from a set of solves, for a given EventFormat
# -------------------------------------------------------------------------------------------------

def __determine_best_single(solves):
    """ Determines the best single in the set of solves. """

    # If all solves are DNF, then DNF is the best we've got
    if all(solve.is_dnf for solve in solves):
        return DNF

    # Otherwise if we have any non-DNF times, return the minimum total time (including penalties)
    # across all non-DNF solves
    return min(solve.get_total_time() for solve in solves if not solve.is_dnf)


def __determine_event_result(single, average, event_format):
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
    """ Returns the best single for these 3 solves, and no average. """

    return __determine_bests_mo3(solves)


def __determine_bests_mo3(solves):
    """ Returns the best single and mean for these 3 solves. """

    # Count how many DNFs are in these solves
    dnf_count = sum(1 for solve in solves if solve.is_dnf)

    # If there are any DNFs at all in a Mo3, the average must be DNF.
    # Otherwise the average is the mean of the 3 solves.
    if dnf_count > 0:
        average = DNF
    else:
        average = round(sum(solve.get_total_time() for solve in solves) / 3.0)

    # If all solves are DNFs, then the best single must be DNF.
    # Otherwise the best single is the minimum time of all non-DNF solves.
    if dnf_count == 3:
        single = DNF
    else:
        single = min(solve.get_total_time() for solve in solves if not solve.is_dnf)

    return single, average


def __determine_bests_ao5(solves):
    """ Returns the best single and average for these 5 solves, where the average
    is the arithmetic mean of the middle 3 solves. """

    # Count how many DNFs are in these solves
    dnf_count = sum(1 for solve in solves if solve.is_dnf)

    # If there are no DNFs at all, the best single is the minimum solve time, and the average
    # is the mean of the middle three (which is the sum of all times, less the best and worse)
    if dnf_count == 0:
        times   = [solve.get_total_time() for solve in solves]
        best    = min(times)
        worst   = max(times)
        average = round((sum(times) - best - worst) / 3.0)

    # If there's exactly 1 DNF, the best single is the minimum of the non-DNF solves, and the
    # average is the mean of the middle three (the sum of all non-DNFs, less the best).
    elif dnf_count == 1:
        times   = [solve.get_total_time() for solve in solves if not solve.is_dnf]
        best    = min(times)
        average = round((sum(times) - best) / 3.0)

    # If all 5 solves are DNFs, the best single and average are both DNF
    elif dnf_count == 5:
        average = DNF
        best    = DNF

    # In all other cases (2, 3, 4 DNFs), the average is a DNF, and the best single is the
    # minimum solve time of the non-DNF solves.
    else:
        times   = [solve.get_total_time() for solve in solves if not solve.is_dnf]
        average = DNF
        best    = min(times)

    return best, average
