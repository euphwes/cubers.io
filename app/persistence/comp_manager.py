""" Utility module for providing access to business logic for competitions, events, etc. """

from collections import OrderedDict
from datetime import datetime

from sqlalchemy.orm import joinedload

from app import DB
from app.persistence.models import Competition, CompetitionEvent, Event, Scramble,\
CompetitionGenResources, UserEventResults, User

# -------------------------------------------------------------------------------------------------

def get_competition_gen_resources():
    """ Gets the current competition generation resources record. """

    return CompetitionGenResources.query.one()


def save_competition_gen_resources(comp_gen_resource):
    """ Saves the competition generation resources record. """

    DB.session.add(comp_gen_resource)
    DB.session.commit()


def get_event_by_name(name):
    """ Returns an event by name. """

    return Event.query.\
        filter(Event.name == name).\
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
        order_by(Event.id)


def get_all_complete_user_results_for_comp(comp_id):
    """ Gets all complete UserEventResults for the specified competition. """

    return DB.session.\
        query(UserEventResults).\
        join(CompetitionEvent).\
        join(Competition).\
        join(Event).\
        filter(Competition.id == comp_id).\
        filter(UserEventResults.is_complete)


def get_all_complete_user_results_for_comp_and_user(comp_id, user_id):
    """ Gets all complete UserEventResults for the specified competition and user. """

    return DB.session.\
        query(UserEventResults).\
        join(User).\
        join(CompetitionEvent).\
        join(Competition).\
        join(Event).\
        filter(Competition.id == comp_id).\
        filter(User.id == user_id).\
        filter(UserEventResults.is_complete).\
        all()


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
    """ Gets all complete UserEventResults for the specified event and user
    i.e all 3x3 results for joe """

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


def get_all_events():
    """ Returns a list of all events. """

    return DB.session.\
        query(Event).\
        order_by(Event.id).\
        all()


def get_events_id_name_mapping():
    """ Returns a dictionary of event ID to name mappings. """

    mapping = OrderedDict()
    for event in get_all_events():
        mapping[event.id] = event.name

    return mapping


def get_all_events_user_has_participated_in(user_id):
    """ Returns a list of all events. """

    return DB.session.\
        query(Event).\
        join(CompetitionEvent).\
        join(UserEventResults).\
        filter(UserEventResults.user_id == user_id).\
        filter(UserEventResults.is_complete).\
        distinct(Event.id).\
        all()


def get_participants_in_competition(comp_id):
    """ Returns a list of all participants in the specified competition. Participant is defined
    as somebody who has any complete UserEventResults in the specified competition. """

    # pylint: disable=C0121
    results = DB.session.\
        query(UserEventResults).\
        join(CompetitionEvent).\
        join(Competition).\
        join(User).\
        filter(Competition.id == comp_id).\
        filter(UserEventResults.single != "PENDING").\
        filter(UserEventResults.reddit_comment != '').\
        filter(UserEventResults.reddit_comment != None).\
        with_entities(User.username).\
        order_by(User.username).\
        distinct()

    # return just a list of names in the competition, not the list of 1-tuples from the query
    return [r[0] for r in results]


def get_complete_competitions():
    """ Returns id and title for all of the inactive competitions. """

    #pylint: disable=C0301
    return Competition.query.\
        with_entities(Competition.id, Competition.title, Competition.active, Competition.start_timestamp, Competition.end_timestamp).\
        filter(Competition.active.is_(False)).\
        order_by(Competition.id.desc()).\
        all()


def get_all_competitions():
    """ Returns all competitions. """

    return DB.session.\
        query(Competition).\
        options(joinedload(Competition.events)).\
        order_by(Competition.id)\
        .all()


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


def get_competition(competition_id):
    """ Get a competition by id """

    return Competition.query.\
        get(competition_id)


def get_competition_by_reddit_id(reddit_id):
    """ Get a competition by reddit thread id """

    return Competition.query.\
        filter(Competition.reddit_thread_id == reddit_id).\
        first()


def save_competition(competition):
    """ Save a modified competition object. """

    DB.session.add(competition)
    DB.session.commit()


def get_comp_event_by_id(comp_event_id):
    """ Returns a competition_event by id. """

    return CompetitionEvent.query.\
        filter(CompetitionEvent.id == comp_event_id).\
        first()


def save_new_competition(title, reddit_id, event_data):
    """ Creates a new active competition, events for that competition, and ensures all the other
    competitions are now inactive. Returns the newly-created competition. """

    now = datetime.utcnow()

    # Ensure all active comps are now inactive (should just be 1, but get them all just in case)
    # Any currently active comp should end now
    for comp in Competition.query.filter(Competition.active).all():
        comp.end_timestamp = now
        comp.active = False

    # Create new active comp starting now
    new_comp = Competition(title=title, reddit_thread_id=reddit_id,
                           active=True, start_timestamp=now)

    for data in event_data:
        event = get_event_by_name(data['name'])
        comp_event = CompetitionEvent(event_id=event.id)

        for scramble_text in data['scrambles']:
            scramble = Scramble(scramble = scramble_text)
            comp_event.scrambles.append(scramble)

        new_comp.events.append(comp_event)

    DB.session.add(new_comp)
    DB.session.commit()

    return new_comp
