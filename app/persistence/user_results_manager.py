""" Utility module for persisting and retrieving UserEventResults """

from app import DB
from app.persistence.comp_manager import get_active_competition
from app.persistence.models import Competition, CompetitionEvent, Event, UserEventResults,\
    User, UserSolve

# -------------------------------------------------------------------------------------------------

class UserEventResultsDoesNotExistException(Exception):
    """ An error raised when an attempting an operation on a UserEventResults
    which does not exist. """

    def __init__(self, results_id):
        self.results_id = results_id
        super(UserEventResultsDoesNotExistException, self).__init__()

    def __str__(self):
        return "There is no UserEventResults with id {}".format(self.results_id)

DEFAULT_BLACKLIST_NOTE = """This result has been manually blacklisted.
If this is an error, please contact a cubers.io admin."""

# -------------------------------------------------------------------------------------------------

def blacklist_results(results_id, note=DEFAULT_BLACKLIST_NOTE):
    """ Blacklists the specified UserEventResults. """

    results = DB.session.\
        query(UserEventResults).\
        filter(UserEventResults.id == results_id).\
        first()

    if not results:
        raise UserEventResultsDoesNotExistException(results_id)

    results.is_blacklisted = True
    results.blacklist_note = note

    DB.session.add(results)
    DB.session.commit()

    return results


def unblacklist_results(results_id):
    """ Unblacklists the specified UserEventResults. """

    results = DB.session.\
        query(UserEventResults).\
        filter(UserEventResults.id == results_id).\
        first()

    if not results:
        raise UserEventResultsDoesNotExistException(results_id)

    results.is_blacklisted = False
    results.blacklist_note = ''

    DB.session.add(results)
    DB.session.commit()

    return results


def get_user_completed_solves_count(user_id):
    """ Returns a count of the number of solves for completed events for the given user. """

    return DB.session.\
        query(UserSolve).\
        join(UserEventResults).\
        filter(UserEventResults.is_complete).\
        filter(UserEventResults.user_id == user_id).\
        distinct(UserSolve.id).\
        count()


def get_comment_id_by_comp_id_and_user(comp_id, user):
    """ Returns a Reddit comment ID for the specified user and competition id. """

    for result in get_all_user_results_for_comp_and_user(comp_id, user.id):
        if result.reddit_comment:
            return result.reddit_comment
    return None


def are_results_different_than_existing(comp_event_results, user):
    """ Determine if these results are identical to any previous existing results for this user
    and this competition event by comparing their times strings and comments. """

    existing_results = get_event_results_for_user(comp_event_results.comp_event_id, user)
    if not existing_results:
        return True

    if existing_results.times_string != comp_event_results.times_string:
        return True

    return existing_results.comment != comp_event_results.comment


def get_event_results_for_user(comp_event_id, user):
    """ Retrieves a UserEventResults for a specific user and competition event. """

    return UserEventResults.query.\
        filter(UserEventResults.user_id == user.id).\
        filter(UserEventResults.comp_event_id == comp_event_id).\
        first()


def get_all_complete_event_results():
    """ Gets all complete event results. """

    return UserEventResults.query.\
        filter(UserEventResults.is_complete).\
        all()


def get_pb_single_event_results_except_current_comp(user_id, event_id):
    """ Returns the UserEventResults which were a PB single for the specified user and event. """

    current_comp_id = get_active_competition().id

    return DB.session.\
        query(UserEventResults).\
        join(User).\
        join(CompetitionEvent).\
        join(Competition).\
        join(Event).\
        filter(Event.id == event_id).\
        filter(User.id == user_id).\
        filter(Competition.id != current_comp_id).\
        filter(UserEventResults.was_pb_single).\
        filter(UserEventResults.is_blacklisted.isnot(True)).\
        filter(UserEventResults.is_complete).\
        order_by(UserEventResults.id).\
        all()


def get_pb_average_event_results_except_current_comp(user_id, event_id):
    """ Returns the UserEventResults which were a PB average for the specified user and event. """

    current_comp_id = get_active_competition().id

    return DB.session.\
        query(UserEventResults).\
        join(User).\
        join(CompetitionEvent).\
        join(Competition).\
        join(Event).\
        filter(Event.id == event_id).\
        filter(User.id == user_id).\
        filter(Competition.id != current_comp_id).\
        filter(UserEventResults.was_pb_average).\
        filter(UserEventResults.is_blacklisted.isnot(True)).\
        filter(UserEventResults.is_complete).\
        order_by(UserEventResults.id).\
        all()


def get_all_complete_user_results_for_comp(comp_id, omit_blacklisted=True):
    """ Gets all complete UserEventResults for the specified competition. """

    results_query = DB.session.\
        query(UserEventResults).\
        join(CompetitionEvent).\
        join(Competition).\
        join(Event).\
        filter(Competition.id == comp_id).\
        filter(UserEventResults.is_complete)

    # Omitting blacklisted means only including results which are *not* True,
    # aka including results where the blacklist flag is False or null/None
    if omit_blacklisted:
        results_query = results_query.filter(UserEventResults.is_blacklisted.isnot(True))

    return results_query


def get_blacklisted_entries_for_comp(comp_id):
    """ Returns a list of tuples of (user_id, event_id) for all blacklisted UserEventResults in
    the specified competition. """

    results = DB.session.\
        query(UserEventResults).\
        join(CompetitionEvent).\
        join(Competition).\
        join(Event).\
        filter(Competition.id == comp_id).\
        filter(UserEventResults.is_complete).\
        filter(UserEventResults.is_blacklisted.is_(True)).\
        all()

    return [(result.user_id, result.CompetitionEvent.event_id) for result in results]


def get_all_complete_user_results_for_comp_and_user(comp_id, user_id, include_blacklisted=True):
    """ Gets all complete UserEventResults for the specified competition and user. Includes
    blacklisted results by default, but can optionally exclude them. """

    results_query = DB.session.\
        query(UserEventResults).\
        join(User).\
        join(CompetitionEvent).\
        join(Competition).\
        join(Event).\
        filter(Competition.id == comp_id).\
        filter(User.id == user_id).\
        filter(UserEventResults.is_complete)

    # If we don't want blacklisted results, filter those out.
    if not include_blacklisted:
        results_query = results_query.filter(UserEventResults.is_blacklisted.isnot(True))

    return results_query.all()


def get_all_user_results_for_comp_and_user(comp_id, user_id):
    """ Gets all UserEventResults for the specified competition and user. """

    return DB.session.\
        query(UserEventResults).\
        join(User).\
        join(CompetitionEvent).\
        join(Competition).\
        join(Event).\
        filter(Competition.id == comp_id).\
        filter(User.id == user_id)


def get_all_complete_user_results_for_user_and_event(user_id, event_id):
    """ Gets all complete UserEventResults for the specified event and user. """

    return DB.session.\
        query(UserEventResults).\
        join(User).\
        join(CompetitionEvent).\
        join(Event).\
        filter(Event.id == event_id).\
        filter(User.id == user_id).\
        filter(UserEventResults.is_complete).\
        order_by(UserEventResults.id).\
        all()


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

    existing_results.single         = new_results.single
    existing_results.average        = new_results.average
    existing_results.result         = new_results.result
    existing_results.comment        = new_results.comment
    existing_results.is_complete    = new_results.is_complete
    existing_results.times_string   = new_results.times_string
    existing_results.was_pb_average = new_results.was_pb_average
    existing_results.was_pb_single  = new_results.was_pb_single
    existing_results.is_blacklisted = new_results.is_blacklisted
    existing_results.blacklist_note = new_results.blacklist_note

    # Update any existing solves with the data coming in from the new solves
    for old_solve in existing_results.solves:
        found = False
        for new_solve in new_results.solves:
            if old_solve.scramble_id == new_solve.scramble_id:
                found = True
                old_solve.time        = new_solve.time
                old_solve.is_dnf      = new_solve.is_dnf
                old_solve.is_plus_two = new_solve.is_plus_two
        if not found:
            DB.session.delete(old_solve)

    # Determine which of the new solves are actually new and add those to the results record
    old_scramble_ids = [solve.scramble_id for solve in existing_results.solves]
    for new_solve in [s for s in new_results.solves if s.scramble_id not in old_scramble_ids]:
        existing_results.solves.append(new_solve)

    DB.session.commit()
    return existing_results


# -------------------------------------------------------------------------------------------------
# Below are functions that aren't normally used in the app, but were used at some point for
# data cleanup with the commands in `commands.py`
# -------------------------------------------------------------------------------------------------

def get_all_null_is_complete_event_results():
    """ Get all UserEventResults with a null is_complete value. """

    # pylint: disable=C0121
    return UserEventResults.query.\
        filter(UserEventResults.is_complete == None).\
        all()


def get_all_na_average_event_results():
    """ Get all UserEventResults where the average is N/A. """

    return UserEventResults.query.\
        filter(UserEventResults.average == 'N/A').\
        all()


def bulk_save_event_results(results_list):
    """ Save a bunch of results at once. """

    for result in results_list:
        DB.session.add(result)
    DB.session.commit()
