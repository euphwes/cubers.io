""" Utility functions to facilitate working with events. """

from app.persistence.models import EventFormat

event_names = {
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

def get_event_name(name):
    if name.lower() in event_names:
        return event_names[name.lower()]
    else:
        return name


def determine_bests(solves, event_format):
    """ docstring here """

    if event_format == EventFormat.Ao5:
        return determine_bests_ao5(solves)


def determine_bests_bo3(solves):
    """ docstring """

    if all(solve.is_dnf for solve in solves):
        return 'DNF'

    else:
        return min(solve.time for solve in solves if not solve.is_dnf)


def determine_bests_mo3(solves):
    """ docstring here """

    dnf_count = sum(1 for solve in solves if solve.is_dnf)

    if dnf_count > 0:
        average = 'DNF'
    else:
        average = sum(solve.time for solve in solves) / 3.0

    if dnf_count == 3:
        single = 'DNF'
    else:
        single = min(solve.time for solve in solves if not solve.is_dnf)

    return single, average


def determine_bests_ao5(solves):
    """ docstring here """

    dnf_count = sum(1 for solve in solves if solve.is_dnf)

    if dnf_count == 0:
        times   = [solve.time for solve in solves]
        best    = min(times)
        worst   = max(times)
        average = int((sum(times) - best - worst) / 3.0)

    elif dnf_count == 1:
        times   = [solve.time for solve in solves if not solve.is_dnf]
        best    = min(times)
        average = int((sum(times) - best) / 3.0)

    elif dnf_count == 5:
        average = 'DNF'
        best    = 'DNF'

    else:
        times   = [solve.time for solve in solves if not solve.is_dnf]
        average = 'DNF'
        best    = min(times)

    return best, average