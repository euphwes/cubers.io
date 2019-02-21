""" Business logic for creating a new competition. """

from datetime import datetime
from math import ceil

from app import CUBERS_APP

from app.persistence.comp_manager import get_competition_gen_resources,\
save_competition_gen_resources, save_new_competition

from app.persistence.events_manager import get_event_by_name,\
    retrieve_from_scramble_pool_for_event

from app.util.events.resources import get_weekly_events, get_bonus_events,\
get_bonus_events_rotation_starting_at, get_COLL_at_index, get_bonus_events_without_current,\
get_num_COLLs, get_num_bonus_events, EVENT_COLL

from app.util.competition.posting import post_competition

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

def generate_new_competition():
    """ Generate a new competition and post to Reddit. """

    # Get the info required to know what events and COLL to do next
    comp_gen_data = get_competition_gen_resources()

    # Figure out next competition number
    comp_gen_data.current_comp_num += 1
    comp_number = comp_gen_data.current_comp_num

    # Determine the competition name
    comp_name = get_comp_name_from_date()

    # Generate scrambles for every weekly event
    event_data = list()
    for weekly_event in get_weekly_events():
        event_data.append(dict({
            'name':      weekly_event.name,
            'scrambles': weekly_event.get_scrambles()
        }))

    # If we're doing all events, just get all of theme
    # if all_events:
    if False:
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
        coll_scrambles = [EVENT_COLL.get_scramble(coll_number) for _ in range(EVENT_COLL.num_scrambles)]
        event_data.append(dict({
            'name':      EVENT_COLL.name,
            'scrambles': [s[0] for s in coll_scrambles],
            'scrambles_for_post': [s[1] for s in coll_scrambles]
        }))

    # Generate scrambles for the bonus events in this comp
    for bonus_event in bonus_events:
        if bonus_event == EVENT_COLL:
            continue
        else:
            scrambles = list()
            bonus_event_dict = dict({
                'name':      bonus_event.name,
                'scrambles': scrambles
            })
        event_data.append(bonus_event_dict)

    # Post competition to reddit
    reddit_id = post_competition(comp_name, comp_number, event_data,\
        bonus_names, upcoming_bonus_names)

    # Save new competition to database
    # TODO: fix relay scrambles for representation in reddit thread
    new_db_competition = save_new_competition(comp_name, reddit_id, event_data)

    # Save competition gen resource to database
    comp_gen_data.previous_comp_id = comp_gen_data.current_comp_id
    comp_gen_data.current_comp_id = new_db_competition.id
    save_competition_gen_resources(comp_gen_data)

    return new_db_competition


def week_of_month(datetime_timestamp):
    """ Returns the week of the month for the specified date. """

    return ceil(datetime_timestamp.day/7)


def get_comp_name_from_date():
    """ Returns a competition name based on the current date. """

    today = datetime.utcnow()
    return COMPETITION_NAME_TEMPLATE.format(
        month = today.strftime('%b'),
        year  = today.year,
        week  = week_of_month(today)
    )


def __get_scrambles_for_event(event, coll=False):
    """ Returns a list of scrambles for the specified event. Source from the scramble pool for
    all events for COLL, which is generated on the fly. """

    if event == EVENT_COLL:
        pass