""" Utility module for persisting and retrieving Competitions, and information related
to Competitions. """

from datetime import datetime
from functools import lru_cache

from sqlalchemy.orm import joinedload

from app import DB
from app.persistence.models import Competition, CompetitionEvent, Event, Scramble,\
    CompetitionGenResources, UserEventResults, User
from app.persistence.events_manager import get_event_by_name

# -------------------------------------------------------------------------------------------------

def get_competition(competition_id):
    """ Get a competition by id """

    return Competition.query.\
        get(competition_id)


def get_competition_by_reddit_id(reddit_id):
    """ Get a competition by reddit thread id """

    return Competition.query.\
        filter(Competition.reddit_thread_id == reddit_id).\
        first()


def get_active_competition():
    """ Get the current active competition. """

    return Competition.query.\
        filter(Competition.active).\
        first()


def get_previous_competition():
    """ Get the previous competition, which is the most recent inactive one. """

    return Competition.query.\
        filter(Competition.active.is_(False)).\
        order_by(Competition.id.desc()).\
        first()


def get_all_comp_events_for_comp(comp_id):
    """ Gets all CompetitionEvents for the specified competition. """

    return DB.session.\
        query(CompetitionEvent).\
        join(Event).\
        filter(CompetitionEvent.competition_id == comp_id).\
        order_by(Event.id).\
        all()


@lru_cache()
def get_comp_event_name_by_id(comp_event_id):
    """ Returns a competition_event's event name by id. """

    return CompetitionEvent.query.\
        filter(CompetitionEvent.id == comp_event_id).\
        first().\
        Event.\
        name


def get_comp_event_by_id(comp_event_id):
    """ Returns a competition_event by id. """

    return CompetitionEvent.query.\
        filter(CompetitionEvent.id == comp_event_id).\
        first()


def get_user_participated_competitions_count(user_id):
    """ Returns a count of the number of competitions a user has participated in. """

    return DB.session.\
        query(Competition).\
        join(CompetitionEvent).\
        join(UserEventResults).\
        filter(UserEventResults.is_complete).\
        filter(UserEventResults.user_id == user_id).\
        distinct(Competition.id).\
        count()


def get_participants_in_competition(comp_id):
    """ Returns a list of all participants in the specified competition. Participant is defined
    as somebody who has any complete UserEventResults in the specified competition. Omit people
    who only have blacklisted results. """

    results = DB.session.\
        query(UserEventResults).\
        join(CompetitionEvent).\
        join(Competition).\
        join(User).\
        filter(Competition.id == comp_id).\
        filter(UserEventResults.is_blacklisted.isnot(True)).\
        filter(UserEventResults.is_complete).\
        with_entities(User.username).\
        order_by(User.username).\
        distinct()

    # return just a list of names in the competition, not the list of 1-tuples from the query
    return [r[0] for r in results]


def get_participants_in_competition_as_user_ids(comp_id):
    """ Returns a list of user IDs for all participants in the specified competition.
    Participant is defined as somebody who has any complete UserEventResults in the specified
    competition. Omit people who only have blacklisted results. """

    results = DB.session.\
        query(UserEventResults).\
        join(CompetitionEvent).\
        join(Competition).\
        join(User).\
        filter(Competition.id == comp_id).\
        filter(UserEventResults.is_blacklisted.isnot(True)).\
        filter(UserEventResults.is_complete).\
        with_entities(User.id).\
        distinct()

    # return just a list of user ids, not the list of 1-tuples from the query
    return [r[0] for r in results]


def get_complete_competitions():
    """ Returns id and title for all of the inactive competitions. """

    return Competition.query.\
        with_entities(Competition.id, Competition.title, Competition.active, Competition.start_timestamp,
                      Competition.end_timestamp).\
        filter(Competition.active.is_(False)).\
        order_by(Competition.id.desc()).\
        all()


def get_all_competitions():
    """ Returns all competitions. """

    return DB.session.\
        query(Competition).\
        options(joinedload(Competition.events)).\
        order_by(Competition.id).\
        all()


def bulk_update_comps(comps):
    """ Updates competitions in bulk. """

    for comp in comps:
        DB.session.add(comp)
    DB.session.commit()


def get_all_competitions_user_has_participated_in(user_id):
    """ Returns all competitions for which the user has posted completed UserEventResults. """

    return DB.session.\
        query(Competition).\
        join(CompetitionEvent).\
        join(UserEventResults).\
        filter(UserEventResults.is_complete).\
        filter(UserEventResults.user_id == user_id).\
        options(joinedload(Competition.events)).\
        order_by(Competition.id).\
        distinct(Competition.id).\
        all()


def save_competition(competition):
    """ Save a modified competition object. """

    DB.session.add(competition)
    DB.session.commit()


def save_new_competition(title, event_data):
    """ Creates a new active competition, events for that competition, and ensures all the other
    competitions are now inactive. Returns the newly-created competition. """

    now = datetime.utcnow()

    # Ensure all active comps are now inactive (should just be 1, but get them all just in case)
    # Any currently active comp should end now
    for comp in Competition.query.filter(Competition.active).all():
        comp.end_timestamp = now
        comp.active = False

    # Create new active comp starting now
    new_comp = Competition(title=title, active=True, start_timestamp=now)

    for data in event_data:
        event = get_event_by_name(data['name'])
        comp_event = CompetitionEvent(event_id=event.id)

        for scramble_text in data['scrambles']:
            scramble = Scramble(scramble=scramble_text)
            comp_event.scrambles.append(scramble)

        new_comp.events.append(comp_event)

    DB.session.add(new_comp)
    DB.session.commit()

    return new_comp

# -------------------------------------------------------------------------------------------------
#              Stuff for CompetitionGenResources, which doesn't need its own file
# -------------------------------------------------------------------------------------------------

def get_competition_gen_resources():
    """ Gets the CompetitionGenResources record. """

    return CompetitionGenResources.query.one()


def save_competition_gen_resources(comp_gen_resource):
    """ Saves the CompetitionGenResources record. """

    DB.session.add(comp_gen_resource)
    DB.session.commit()


def override_title_for_next_comp(title):
    """ Sets an override title for the upcoming competition. """

    resources = get_competition_gen_resources()
    resources.title_override = title

    save_competition_gen_resources(resources)


def set_all_events_flag_for_next_comp(all_events):
    """ Sets the all_events flag for the upcoming competition """

    resources = get_competition_gen_resources()
    resources.all_events = all_events

    save_competition_gen_resources(resources)
