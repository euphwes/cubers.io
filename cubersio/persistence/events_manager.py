""" Utility module for persisting and retrieving Events, and information related to Events. """

from collections import OrderedDict
from functools import lru_cache

from cubersio import DB
from cubersio.persistence.models import Event, CompetitionEvent, UserEventResults, ScramblePool
from cubersio.util.events.resources import WCA_EVENTS, NON_WCA_EVENTS, BONUS_EVENTS


def get_event_by_name(name):
    """ Returns an event by name. """

    return Event.query.\
        filter(Event.name == name).\
        first()


def get_all_events():
    """ Returns a list of all events. """

    return DB.session.\
        query(Event).\
        order_by(Event.id).\
        all()


@lru_cache()
def get_event_format_for_event(event_id):
    """ Gets the event format for the specified event. """

    return Event.query.\
        filter(Event.id == event_id).\
        first().\
        eventFormat


def get_all_WCA_events():
    """ Returns a list of all WCA events. """

    wca_names = set(e.name for e in WCA_EVENTS)
    return [e for e in get_all_events() if e.name in wca_names]


def get_all_non_WCA_events():
    """ Returns a list of all non-WCA events. """

    non_wca_names = set(e.name for e in NON_WCA_EVENTS)
    return [e for e in get_all_events() if e.name in non_wca_names]


def get_all_bonus_events():
    """ Returns a list of all bonus events. """

    bonus_event_names = set(e.name for e in BONUS_EVENTS)
    return [e for e in get_all_events() if e.name in bonus_event_names]


def get_events_name_id_mapping():
    """ Returns a dictionary of event name to ID mappings. """

    mapping = OrderedDict()
    for event in get_all_events():
        mapping[event.name] = event.id

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


def retrieve_from_scramble_pool_for_event(event_id, num_scrambles):
    """ Retrieves the desired number of scrambles from the scramble pool for the specified event. """

    return DB.session.\
        query(ScramblePool).\
        filter(ScramblePool.event_id == event_id).\
        limit(num_scrambles).\
        all()


def delete_from_scramble_pool(scrambles):
    """ Deletes the specified scrambles from the scramble pool. """

    for scramble in scrambles:
        DB.session.delete(scramble)

    DB.session.commit()


def add_scramble_to_scramble_pool(scramble, event_id):
    """ Adds a scramble to the scramble pool for the specified event. """

    DB.session.add(ScramblePool(scramble=scramble, event_id=event_id))
    DB.session.commit()
