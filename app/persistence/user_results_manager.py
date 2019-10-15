""" Utility module for persisting and retrieving UserEventResults """

from sqlalchemy.orm import joinedload

from app import DB
from app.persistence.comp_manager import get_active_competition
from app.persistence.models import Competition, CompetitionEvent, Event, UserEventResults,\
    User, UserSolve

from psycopg2.errors import UniqueViolation

# -------------------------------------------------------------------------------------------------

class UserEventResultsDoesNotExistException(Exception):
    """ An error raised when an attempting an operation on a UserEventResults
    which does not exist. """

    def __init__(self, results_id):
        self.results_id = results_id
        super(UserEventResultsDoesNotExistException, self).__init__()

    def __str__(self):
        return "There is no UserEventResults with id {}".format(self.results_id)

# -------------------------------------------------------------------------------------------------

def blacklist_results(results_id, note):
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


def get_user_event_results_by_id(user_event_results_id):
    """ Returns a specific UserEventResults record by ID. """

    return DB.session.\
        query(UserEventResults).\
        filter(UserEventResults.is_complete).\
        filter(UserEventResults.id == user_event_results_id).\
        first()


def get_user_completed_solves_count(user_id):
    """ Returns a count of the number of solves for completed events for the given user. """

    return DB.session.\
        query(UserSolve).\
        join(UserEventResults).\
        filter(UserEventResults.is_complete).\
        filter(UserEventResults.user_id == user_id).\
        distinct(UserSolve.id).\
        count()


def get_user_medals_count(user_id):
    """ Returns a tuple containing the counts of the number of gold, silver, and bronze medals
    this user has. """

    bronze_count = DB.session.query(UserEventResults).\
        filter(UserEventResults.user_id == user_id).\
        filter(UserEventResults.was_bronze_medal).\
        count()

    silver_count = DB.session.query(UserEventResults).\
        filter(UserEventResults.user_id == user_id).\
        filter(UserEventResults.was_silver_medal).\
        count()

    gold_count = DB.session.query(UserEventResults).\
        filter(UserEventResults.user_id == user_id).\
        filter(UserEventResults.was_gold_medal).\
        count()

    return (gold_count, silver_count, bronze_count)


def get_user_solve_for_scramble_id(user_id, scramble_id):
    """ Returns a specific user solve for the given user ID and scramble ID. """

    return DB.session.\
        query(UserSolve).\
        join(UserEventResults).\
        filter(UserEventResults.user_id == user_id).\
        filter(UserSolve.scramble_id == scramble_id).\
        count()


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


def get_results_for_comp_event(comp_event_id):
    """ Retrieves all UserEventResults for the specified comp event. """

    # Get all complete, unblacklisted results for the specified comp_event_id
    return DB.session.\
        query(UserEventResults).\
        join(CompetitionEvent).\
        filter(CompetitionEvent.id == comp_event_id).\
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
        filter(Competition.id == comp_id).\
        filter(UserEventResults.is_complete)

    # Omitting blacklisted means only including results which are *not* True,
    # aka including results where the blacklist flag is False or null/None
    if omit_blacklisted:
        results_query = results_query.filter(UserEventResults.is_blacklisted.isnot(True))

    return results_query


def get_all_complete_user_results_for_comp_event(comp_event_id, omit_blacklisted=True):
    """ Gets all complete UserEventResults for the specified CompetitionEvent. """

    results_query = DB.session.\
        query(UserEventResults).\
        join(CompetitionEvent).\
        filter(CompetitionEvent.id == comp_event_id).\
        filter(UserEventResults.is_complete)

    # Omitting blacklisted means only including results which are *not* True,
    # aka including results where the blacklist flag is False or null/None
    if omit_blacklisted:
        results_query = results_query.filter(UserEventResults.is_blacklisted.isnot(True))

    results_query = results_query.\
        options(joinedload(UserEventResults.User)).\
        options(joinedload(UserEventResults.CompetitionEvent).subqueryload(CompetitionEvent.Event))

    return results_query.all()


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

    # Make sure the events get ordered in a predictable way
    results_query = results_query.order_by(Event.id)

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


def save_event_results(comp_event_results):
    """ Saves a UserEventResults record. """

    DB.session.add(comp_event_results)

    try:
        DB.session.commit()
    except UniqueViolation as ex:
        # This is probably because of duplicate UserSolve records with same scramble_id
        # and user_event_results_id.
        # Since we're rewriting all this soon anyway, this is good enough for now.
        # Let's do it better next time.
        print(str(ex))
        pass

    DB.session.expunge(comp_event_results)

    return comp_event_results


def delete_event_results(comp_event_results):
    """ Deletes a UserEventResults record. """

    DB.session.delete(comp_event_results)
    DB.session.commit()


def delete_user_solve(user_solve):
    """ Deletes a user solve. """

    DB.session.delete(user_solve)
    DB.session.commit()


def bulk_save_event_results(results_list):
    """ Save a bunch of results at once. """

    for result in results_list:
        DB.session.add(result)
    DB.session.commit()
