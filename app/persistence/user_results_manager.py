""" Utility module for providing access to business logic for user solves. """

from app import DB
from app.persistence.models import UserEventResults, UserSolve
from app.util.events_util import determine_bests

from .comp_manager import get_comp_event_by_id

# -------------------------------------------------------------------------------------------------

def build_user_event_results(comp_event_id, solves, comment):
    """ Builds a UserEventsResult object from a competition_event ID and a list of scrambles
    and associated solve times. """

    comp_event = get_comp_event_by_id(comp_event_id)
    results = UserEventResults(comp_event_id=comp_event_id, comment=comment)

    for solve in solves:
        time = solve['time']
        if not time:
            # time is literally zero, meaning user didn't submit a time for this solve
            continue

        dnf         = solve['isDNF']
        time        = 0 if dnf else int(float(solve['time']) * 100)
        plus_two    = solve['isPlusTwo']
        scramble_id = solve['id']

        user_solve = UserSolve(time=time, is_dnf=dnf, is_plus_two=plus_two, scramble_id=scramble_id)
        results.solves.append(user_solve)

    num_expected_solves = comp_event.Event.totalSolves
    if len(results.solves) < num_expected_solves:
        results.single = 'PENDING'
        results.average = 'PENDING'
    else:
        single, average = determine_bests(results.solves, comp_event.Event.eventFormat)
        results.single  = single
        results.average = average

    return results


def save_event_results_for_user(comp_event_results, user):
    """ Associates a UserEventResults with a specific user and saves it to the database. """

    comp_event_results.user_id = user.id

    DB.session.add(comp_event_results)
    DB.session.commit()

    return comp_event_results
