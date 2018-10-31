""" Utility functions to facilitate working with events. """

from app.persistence.models import EventFormat

DNF = 'DNF'
NA  = 'N/A'

# -------------------------------------------------------------------------------------------------


def determine_best_single(solves):
    """ Determines the best single in the set of solves. """

    if all(solve.is_dnf for solve in solves):
        return DNF

    return min(solve.get_total_time() for solve in solves if not solve.is_dnf)


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
        return DNF, NA

    return solve.get_total_time(), NA


def determine_bests_bo3(solves):
    """ Returns the best single for these 3 solves, and 'N/A' for the average. """

    if all(solve.is_dnf for solve in solves):
        return DNF, NA

    return min(solve.get_total_time() for solve in solves if not solve.is_dnf), NA


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

# -------------------------------------------------------------------------------------------------
# TODO: Figure out if stuff below is needed. Does it belong in the scripts source? If so, doesn't
# belong directly here in the web app
# -------------------------------------------------------------------------------------------------

EVENT_NAMES = {
    "5x5": "5x5x5",
    "6x6": "6x6x6",
    "7x7": "7x7x7",
    "3x3 relay": "3x3 Relay of 3",
    "relay of 3": "3x3 Relay of 3",
    "4x4oh": "4x4 OH",
    "pyra": "Pyraminx",
    "blind": "3BLD",
    "f2l": "F2L",
    "bld": "3BLD",
    "pll time attack": "PLL Time Attack",
    "3x3 with feet": "3x3 With Feet",
    "3x3 oh": "3x3OH",
    "oll": "OH OLL",
    "mirror blocks": "3x3 Mirror Blocks/Bump",
    "3x3 mirror blocks/bump": "3x3 Mirror Blocks/Bump",
    "3x3 mirror blocks": "3x3 Mirror Blocks/Bump",
    "mirror blocks/bump": "3x3 Mirror Blocks/Bump"
}

def get_friendly_event_name(name):
    """ Get a user-friendly display name for events. """
    if name.lower() in EVENT_NAMES:
        return EVENT_NAMES[name.lower()]
    else:
        return name
