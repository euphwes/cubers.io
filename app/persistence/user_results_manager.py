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
        time        = int(solve['time'])
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


def get_event_results_for_user(comp_event_id, user):
    """ Retrieves a UserEventResults for a specific user and competition event. """
    return UserEventResults.query.filter(UserEventResults.user_id == user.id)\
                                 .filter(UserEventResults.comp_event_id == comp_event_id)\
                                 .first()


def save_event_results_for_user(comp_event_results, user):
    """ Associates a UserEventResults with a specific user and saves it to the database.
    If the user already has an EventResults for this competition, update it instead. """

    # if an existing record exists, update that
    existing_results = get_event_results_for_user(comp_event_results.comp_event_id, user)
    if existing_results:
        return __save_existing_event_results(existing_results, comp_event_results)

    # Otherwise associate the new results with this user and save and commit
    comp_event_results.user_id = user.id
    DB.session.add(comp_event_results)
    DB.session.commit()

    return comp_event_results

def __save_existing_event_results(existing_results, new_results):
    """ Update the existing UserEventResults and UserSolves with the new data. """

    existing_results.single = new_results.single
    existing_results.average = new_results.average
    existing_results.comment = new_results.comment
    existing_results.reddit_comment = new_results.reddit_comment
    for solve in existing_results.solves:
        DB.session.delete(solve)
    for solve in new_results.solves:
        existing_results.solves.append(solve)
    DB.session.commit()
    return existing_results
