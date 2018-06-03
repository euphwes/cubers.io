""" Utility module for providing access to business logic for user solves. """

from app import DB
from app.persistence.models import User, UserEventResults, UserSolve, EventFormat

from .comp_manager import get_comp_event_by_id

# -------------------------------------------------------------------------------------------------

def build_user_event_results(comp_event_id, solves):
    """ Builds a UserEventsResult object from a competition_event ID and a list of scrambles
    and associated solve times. """

    comp_event = get_comp_event_by_id(comp_event_id)
    results = UserEventResults(comp_event_id=comp_event_id)

    for solve in solves:
        time = solve['time']
        if not time:
            # time is literally zero, meaning user didn't submit a time for this solve
            continue

        dnf = solve['isDNF']
        time = 0 if dnf else int(solve['time'] * 100)
        plus_two = solve['plusTwo']

        user_solve = UserSolve(time=time, is_dnf=dnf, is_plus_two=plus_two)
        results.solves.append(user_solve)

    single, average = determine_bests(results.solves, comp_event.event.eventFormat)

    return results


def determine_bests(solves, event_format):
    """ docstring here """

    if event_format == EventFormat.Ao5:
        return determine_bests_Ao5(solves)


def determine_bests_Ao5(solves):
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



def save_event_results_for_user(comp_event_results, user):
    """ Associates a UserEventResults with a specific user and saves it to the database. """

    comp_event_results.user_id = user.id

    DB.session.add(comp_event_results)
    DB.session.commit()

    return comp_event_results