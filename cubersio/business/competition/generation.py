""" Business logic for creating a new competition. """

from datetime import datetime
from math import ceil

from cubersio import app
from cubersio.persistence.comp_manager import get_competition_gen_resources,\
    save_competition_gen_resources, save_new_competition
from cubersio.persistence.events_manager import retrieve_from_scramble_pool_for_event,\
    get_events_name_id_mapping, delete_from_scramble_pool
from cubersio.persistence.models import CompetitionGenResources
from cubersio.util.events.resources import get_bonus_events_rotation_starting_at,\
    BONUS_EVENTS, EVENT_COLL, COLL_LIST, WEEKLY_EVENTS

# -------------------------------------------------------------------------------------------------

# This determines how many bonus events are run in a regular weekly competition.
BONUS_EVENT_COUNT = 8

# Jan 2019 Week 1
# Apr 2021 Week 3, etc
COMPETITION_NAME_TEMPLATE = '{month} {year} Week {week}'

# Make sure we can quickly tell by looking at the title if the competition is just a test one.
IS_DEVO = app.config['IS_DEVO']
if IS_DEVO:
    COMPETITION_NAME_TEMPLATE = '[TEST] ' + COMPETITION_NAME_TEMPLATE

# -------------------------------------------------------------------------------------------------

def generate_new_competition():
    """ Generate a new competition. """

    # Get the info required to know what events and COLL to do next
    comp_gen_data: CompetitionGenResources = get_competition_gen_resources()
    was_all_events: bool = comp_gen_data.all_events

    # Increment competition number. We're not using this anywhere at the moment now that
    # we're not posting competition threads to Reddit, but let's keep track anyway in case
    # we might like the info in the future.
    comp_gen_data.current_comp_num += 1

    # Determine the competition name. If there is a title override in the competition generation
    # data, use that for this week and then empty it so it doesn't apply to next week also.
    # If there is no title override, just use the default naming scheme
    if comp_gen_data.title_override:
        comp_name = comp_gen_data.title_override
        comp_gen_data.title_override = ''
    else:
        comp_name = get_comp_name_from_date()

    # Get the weekly and bonus events for this week
    bonus_events  = get_bonus_events(comp_gen_data)

    # Get the list of events data/scrambles for every event
    event_data = get_events_data(WEEKLY_EVENTS, bonus_events, comp_gen_data)

    # Save new competition to database
    new_db_competition = save_new_competition(comp_name, event_data)

    # Save competition gen resource to database
    comp_gen_data.previous_comp_id = comp_gen_data.current_comp_id
    comp_gen_data.current_comp_id = new_db_competition.id
    save_competition_gen_resources(comp_gen_data)

    return new_db_competition, was_all_events


def week_of_month(datetime_timestamp):
    """ Returns the week of the month for the specified date. """

    return ceil(datetime_timestamp.day / 7)


def get_comp_name_from_date():
    """ Returns a competition name based on the current date. """

    today = datetime.utcnow()
    return COMPETITION_NAME_TEMPLATE.format(
        month=today.strftime('%b'),
        year=today.year,
        week=week_of_month(today)
    )


def get_bonus_events(comp_gen_data):
    """ Returns the correct subset of bonus events for this week, based on whether or not we're
    doing all events or just continuing the normal weekly rotation. """

    # If the comp gen data says we're doing all events, return all the bonus events and reset
    # the flag so next week's bonus event behavior falls back to default
    if comp_gen_data.all_events:
        comp_gen_data.all_events = False
        update_coll_info(comp_gen_data)  # Make sure the COLL index has been updated
        return BONUS_EVENTS

    # Update start index for bonus events by moving the start index up by BONUS_EVENT_COUNT
    # and then doing a modulus on number of bonus events, to make sure we're starting within
    # the bounds of the bonus events. Get the next BONUS_EVENT_COUNT bonus events starting at
    # the new starting index
    else:
        new_index = (comp_gen_data.current_bonus_index + BONUS_EVENT_COUNT) % len(BONUS_EVENTS)
        comp_gen_data.current_bonus_index = new_index
        bonus_events = get_bonus_events_rotation_starting_at(new_index, BONUS_EVENT_COUNT)
        if EVENT_COLL in bonus_events:
            update_coll_info(comp_gen_data)  # Make sure the COLL index has been updated
        return bonus_events


def update_coll_info(comp_gen_data):
    """ Updates the comp_gen_data's COLL info to point to the next. """

    comp_gen_data.current_OLL_index = (comp_gen_data.current_OLL_index + 1) % len(COLL_LIST)


def get_events_data(weekly_events, bonus_events, comp_gen_data):
    """ Returns a list of dicts containing events data (scrambles lists, event IDs, etc). """

    events_name_id_map = get_events_name_id_mapping()

    events_data = list()

    for events_list in [weekly_events, bonus_events]:
        for event in events_list:
            event_id = events_name_id_map[event.name]

            if event == EVENT_COLL:
                coll = COLL_LIST[comp_gen_data.current_OLL_index]
                events_data.append(dict({
                    'name':      event.name,
                    'event_id':  event_id,
                    'scrambles': [EVENT_COLL.get_scramble(coll) for _ in range(event.num_scrambles)],
                }))

            else:
                events_data.append(dict({
                    'name':      event.name,
                    'event_id':  event_id,
                    'scrambles': get_scrambles_for_event(event_id, event.num_scrambles),
                }))

    return events_data


def get_scrambles_for_event(event_id, num_scrambles):
    """ Returns a list of scrambles for the specified event, sourced from the scramble pool. """

    pregenerated_scrambles = retrieve_from_scramble_pool_for_event(event_id, num_scrambles)
    scramble_list = [pregen.scramble for pregen in pregenerated_scrambles]

    delete_from_scramble_pool(pregenerated_scrambles)

    return scramble_list
