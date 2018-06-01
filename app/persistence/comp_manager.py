""" Utility module for providing access to business logic for users. """

import json
from datetime import datetime

from app import DB
from app.persistence.models import Competition, CompetitionEvent, Event

# -------------------------------------------------------------------------------------------------

def get_event_by_name(name):
    """ Returns an event by name. """
    return Event.query.filter(Event.name == name).first()


def get_active_competition():
    """ Get the current active competition. """
    return Competition.query.filter(Competition.active).first()


def create_new_competition(title, reddit_id, event_data):
    """ Creates a new active competition, events for that competition, and ensures all the other
    competitions are now inactive. Returns the newly created competition. """

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
        scrambles = json.dumps(data['scrambles'])
        comp_event = CompetitionEvent(event=event, scrambles=scrambles)
        new_comp.events.add(comp_event)

    DB.session.add(new_comp)
    DB.session.commit()

    return new_comp
