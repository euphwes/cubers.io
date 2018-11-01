""" Utility functions to facilitate working with events. """

from app.persistence.models import EventFormat

DNF = 'DNF'

# -------------------------------------------------------------------------------------------------

def determine_best_single(solves):
    """ Determines the best single in the set of solves. """

    if all(solve.is_dnf for solve in solves):
        return DNF

    return min(solve.get_total_time() for solve in solves if not solve.is_dnf)


def determine_event_result(single, average_or_mean, event_format):
    """ Returns the correct overall result (either single or average_or_mean)
    based on the event format. """

    results_dict = {
        EventFormat.Ao5: average_or_mean,
        EventFormat.Mo3: average_or_mean,
        EventFormat.Bo3: single,
        EventFormat.Bo1: single,
    }

    try:
        return results_dict[event_format]
    except KeyError:
        raise ValueError(event_format, '{event_format} is not a valid event format.')


def determine_bests(solves, event_format):
    """ Returns a tuple of (best single, average) for these solves based on the supplied
    event format." """

    bests_func_dict = {
        EventFormat.Ao5: determine_bests_ao5,
        EventFormat.Mo3: determine_bests_mo3,
        EventFormat.Bo3: determine_bests_bo3,
        EventFormat.Bo1: determine_bests_bo1,
    }

    try:
        return bests_func_dict[event_format](solves)
    except KeyError:
        raise ValueError(event_format, '{event_format} is not a valid event format.')


def determine_bests_bo1(solves):
    """ Returns just the one single. """

    solve = solves[0]

    if solve.is_dnf:
        return DNF, ''

    return solve.get_total_time(), ''


def determine_bests_bo3(solves):
    """ Returns the best single for these 3 solves, and 'N/A' for the average. """
    return determine_bests_mo3(solves)


def determine_bests_mo3(solves):
    """ Returns the best single and mean for these 3 solves. """

    dnf_count = sum(1 for solve in solves if solve.is_dnf)

    if dnf_count > 0:
        average = DNF
    else:
        average = int(sum(solve.get_total_time() for solve in solves) / 3.0)

    if dnf_count == 3:
        single = DNF
    else:
        single = min(solve.get_total_time() for solve in solves if not solve.is_dnf)

    return single, average


def determine_bests_ao5(solves):
    """ Returns the best single and average for these 5 solves, where the average
    is the arithmetic mean of the middle 3 solves. """

    dnf_count = sum(1 for solve in solves if solve.is_dnf)

    if dnf_count == 0:
        times   = [solve.get_total_time() for solve in solves]
        best    = min(times)
        worst   = max(times)
        average = int((sum(times) - best - worst) / 3.0)

    elif dnf_count == 1:
        times   = [solve.get_total_time() for solve in solves if not solve.is_dnf]
        best    = min(times)
        average = int((sum(times) - best) / 3.0)

    elif dnf_count == 5:
        average = DNF
        best    = DNF

    else:
        times   = [solve.get_total_time() for solve in solves if not solve.is_dnf]
        average = DNF
        best    = min(times)

    return best, average
