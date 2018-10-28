""" Utility module for providing access to business logic for user solves. """

from app import DB
from app.persistence.models import UserEventResults, UserSolve
from app.util.events_util import determine_bests

from .comp_manager import get_comp_event_by_id

# -------------------------------------------------------------------------------------------------


def determine_if_resubmit(user_results, user):
    """ Determines if user has already submitted results to Reddit for this competition. Returns the
    Reddit comment ID if it is a resubmission, or None if it is new. """
    for result in user_results:
        prev_result = get_event_results_for_user(result.comp_event_id, user)
        if prev_result and prev_result.reddit_comment:
            return prev_result.reddit_comment
    return None


def build_all_user_results(user_events_dict):
    """ Builds a list of all UserEventsResult objects, from a dictionary of comp event ID and a
    list of scrambles and associated solve times. (this dict comes from front-end) """

    user_results = list()

    for comp_event_id, comp_event_dict in user_events_dict.items():
        solves = comp_event_dict['scrambles']
        comment = comp_event_dict.get('comment', '')
        event_results = build_user_event_results(comp_event_id, solves, comment)
        user_results.append(event_results)

    return user_results


def build_user_event_results(comp_event_id, solves, comment):
    """ Builds a UserEventsResult object from a competition_event ID and a list of scrambles
    and associated solve times. """

    comp_event = get_comp_event_by_id(comp_event_id)
    results = UserEventResults(comp_event_id=comp_event_id, comment=comment)

    for solve in solves:
        time = solve['time']
        if not time:
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

    # Update any existing solves with the data coming in from the new solves
    for old_solve in existing_results.solves:
        for new_solve in new_results.solves:
            if old_solve.scramble_id == new_solve.scramble_id:
                old_solve.time        = new_solve.time
                old_solve.is_dnf      = new_solve.is_dnf
                old_solve.is_plus_two = new_solve.is_plus_two

    # Determine which of the "new" solves are actually new and add those to the UserEventResults record
    old_scramble_ids = [solve.scramble_id for solve in existing_results.solves]
    for new_solve in [s for s in new_results.solves if s.scramble_id not in old_scramble_ids]:
        existing_results.solves.append(new_solve)

    DB.session.commit()
    return existing_results
