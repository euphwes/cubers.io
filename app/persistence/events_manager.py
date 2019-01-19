""" Utility module for persisting and retrieving Events, and information related to Events. """

from collections import OrderedDict

from app import DB
from app.persistence.models import Event, CompetitionEvent, UserEventResults
from app.util.events_resources import get_WCA_event_names, get_non_WCA_event_names

# -------------------------------------------------------------------------------------------------

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


def get_event_format_for_event(event_id):
    """ Gets the event format for the specified event. """

    return Event.query.\
        filter(Event.id == event_id).\
        first().\
        eventFormat


# pylint: disable=C0103
def get_all_WCA_events():
    """ Returns a list of all WCA events. """

    wca_names = set(get_WCA_event_names())
    return [e for e in get_all_events() if e.name in wca_names]


# pylint: disable=C0103
def get_all_non_WCA_events():
    """ Returns a list of all non-WCA events. """

    non_wca_names = set(get_non_WCA_event_names())
    return [e for e in get_all_events() if e.name in non_wca_names]


def get_events_id_name_mapping():
    """ Returns a dictionary of event ID to name mappings. """

    mapping = OrderedDict()
    for event in get_all_events():
        mapping[event.id] = event.name

    return mapping


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
