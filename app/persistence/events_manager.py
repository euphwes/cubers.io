""" Utility module for persisting and retrieving Events, and information related to Events. """

from collections import OrderedDict

from app import DB
from app.persistence.models import CompetitionEvent, Event, UserEventResults

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
