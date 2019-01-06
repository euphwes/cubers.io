""" Logic for creating a new competition based on the last one. """

from datetime import datetime

from app import CUBERS_APP

from app.persistence.comp_manager import get_competition_gen_resources,\
save_competition_gen_resources, save_new_competition

from app.util.events_resources import get_weekly_events, get_bonus_events,\
get_bonus_events_rotation_starting_at, get_COLL_at_index, get_bonus_events_without_current,\
get_num_COLLs, get_num_bonus_events, EVENT_COLL, EVENT_234Relay, EVENT_333Relay

from app.util.post_comp import post_competition

# -------------------------------------------------------------------------------------------------

# This determines how many bonus events are run in a regular weekly competition.
BONUS_EVENT_COUNT = 5

# Jan 2019 Week 1
# Apr 2021 Week 3, etc
COMPETITION_NAME_TEMPLATE = '{month} {year} Week {week}'

# Make sure we can quickly tell by looking at the title if the competition is just a test one.
IS_DEVO = CUBERS_APP.config['IS_DEVO']
if IS_DEVO:
    COMPETITION_NAME_TEMPLATE = '[TEST] ' + COMPETITION_NAME_TEMPLATE

# -------------------------------------------------------------------------------------------------

def generate_new_competition(all_events=False, title=None):
    """ Generate a new competition and post to Reddit. """

    # Get the info required to know what events and COLL to do next
    comp_gen_data = get_competition_gen_resources()

    # Figure out next competition number
    comp_gen_data.current_comp_num += 1
    comp_number = comp_gen_data.current_comp_num

    # Determine the competition name
    comp_name = title if title else get_comp_name_from_date()

    # Generate scrambles for every WCA event
    event_data = []
    for weekly_event in get_weekly_events():
        event_data.append(dict({
            'name':      weekly_event.name,
            'scrambles': weekly_event.get_scrambles()
        }))

    # If we're doing all events, just get all of theme
    if all_events:
        bonus_events = get_bonus_events()

    # Update start index for bonus events by moving the start index up by BONUS_EVENT_COUNT
    # and then doing a modulus on number of bonus events, to make sure we're starting within
    # the bounds of the bonus events. Get the next BONUS_EVENT_COUNT bonus events starting at
    # the new starting index
    else:
        new_index = (comp_gen_data.current_bonus_index + BONUS_EVENT_COUNT) % get_num_bonus_events()
        comp_gen_data.current_bonus_index = new_index
        bonus_events = get_bonus_events_rotation_starting_at(new_index, BONUS_EVENT_COUNT)

    bonus_names  = [e.name for e in bonus_events]

    # Get list of names of upcoming bonus events
    upcoming_bonus_names = [e.name for e in get_bonus_events_without_current(bonus_events)]
    if not upcoming_bonus_names:
        upcoming_bonus_names = ["Back to the normal rotation next week."]

    # Get the next COLL index and number if we're doing COLL this week
    if EVENT_COLL in bonus_events:
        comp_gen_data.current_OLL_index = (comp_gen_data.current_OLL_index + 1) % get_num_COLLs()
        coll_index  = comp_gen_data.current_OLL_index
        coll_number = get_COLL_at_index(coll_index)

    # Generate scrambles for the bonus events in this comp
    for bonus_event in bonus_events:
        if bonus_event == EVENT_COLL:
            scrambles = bonus_event.get_scrambles(coll_number)
        else:
            scrambles = bonus_event.get_scrambles()
        event_data.append(dict({
            'name':      bonus_event.name,
            'scrambles': scrambles
        }))

    # Post competition to reddit
    reddit_id = post_competition(comp_name, comp_number, event_data,\
        bonus_names, upcoming_bonus_names)

    # Save new competition to database
    event_data = correct_relays_scrambles_for_database(event_data)
    new_db_competition = save_new_competition(comp_name, reddit_id, event_data)

    # Save competition gen resource to database
    comp_gen_data.previous_comp_id = comp_gen_data.current_comp_id
    comp_gen_data.current_comp_id = new_db_competition.id
    save_competition_gen_resources(comp_gen_data)


def week_of_month(datetime_timestamp):
    """ Returns the week of the month for the specified date. """

    from math import ceil
    first_day = datetime_timestamp.replace(day=1)
    dom = datetime_timestamp.day
    adjusted_dom = dom + first_day.weekday()
    return int(ceil(adjusted_dom/7.0))


def get_comp_name_from_date():
    """ Returns a competition name based on the current date. """

    today = datetime.utcnow()
    return COMPETITION_NAME_TEMPLATE.format(
        month = today.strftime('%b'),
        year  = today.year,
        week  = week_of_month(today)
    )

#pylint: disable=C0103
def correct_relays_scrambles_for_database(event_data):
    """ The relay events should display the scrambles as 3 individual scrambles for the
    Reddit competition post, but just one 'triple scramble' for the database. Fix that here. """

    for event in event_data:
        if event['name'] == EVENT_333Relay.name:
            event['scrambles'] = ['1: {}\n2: {}\n3: {}'.format(*event['scrambles'])]
        if event['name'] == EVENT_234Relay.name:
            event['scrambles'] = ['2x2: {}\n3x3: {}\n4x4: {}'.format(*event['scrambles'])]

    return event_data
