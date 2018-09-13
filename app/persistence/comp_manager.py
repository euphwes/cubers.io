""" Utility module for providing access to business logic for competitions, events, etc. """

from datetime import datetime

from app import DB
from app.persistence.models import Competition, CompetitionEvent, Event, Scramble,\
CompetitionGenResources

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
    return Event.query.filter(Event.name == name).first()


def get_active_competition():
    """ Get the current active competition. """
    return Competition.query.filter(Competition.active).first()


def get_competition(competition_id):
    """ Get a competition by id """
    return Competition.query.get(competition_id)


def get_comp_event_by_id(comp_event_id):
    """ Returns a competition_event by id. """
    return CompetitionEvent.query.filter(CompetitionEvent.id == comp_event_id).first()


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
        comp_event = CompetitionEvent(event_id=event.id)

        for scramble_text in data['scrambles']:
            scramble = Scramble(scramble = scramble_text)
            comp_event.scrambles.append(scramble)

        new_comp.events.append(comp_event)

    DB.session.add(new_comp)
    DB.session.commit()

    return new_comp
