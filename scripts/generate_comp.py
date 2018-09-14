""" Logic for creating a new competition based on the last one. """

from app.persistence.comp_manager import get_competition_gen_resources,\
save_competition_gen_resources, create_new_competition

from scripts.events_resources import get_WCA_events, get_non_WCA_events,\
get_bonus_events_rotation_starting_at, get_COLL_at_index, get_bonus_events_without_current,\
get_num_COLLs, get_num_bonus_events, EVENT_COLL

from post_comp import post_competition

# -------------------------------------------------------------------------------------------------

BONUS_EVENT_COUNT = 5
COMPETITION_NAME_TEMPLATE = 'Cubing Competition {}!'

# -------------------------------------------------------------------------------------------------

def generate_new_competition():
    """ Generate a new competition object based on the previous one. """

    # Get the info required to know what events and COLL to do next
    comp_gen_data = get_competition_gen_resources()

    # Figure out next competition number and name
    comp_gen_data.current_comp_num += 1
    comp_number = comp_gen_data.current_comp_num
    comp_name = COMPETITION_NAME_TEMPLATE.format(comp_number)

    # Generate scrambles for every WCA event
    event_data = []
    for wca_event in get_WCA_events():
        event_data.append(dict({
            'name':      wca_event.name,
            'scrambles': wca_event.get_scrambles()
        }))

    # Update start index for bonus events and get the list of bonus events
    comp_gen_data.current_bonus_index = (comp_gen_data.current_bonus_index + BONUS_EVENT_COUNT) % get_num_bonus_events()
    bonus_index  = comp_gen_data.current_bonus_index
    bonus_events = get_bonus_events_rotation_starting_at(bonus_index, BONUS_EVENT_COUNT)
    bonus_names  = [e.name for e in bonus_events]

    # Get list of names of upcoming bonus events
    upcoming_bonus_names = [e.name for e in get_bonus_events_without_current(bonus_events)]

    # Get the next COLL index and number if we're doing COLL this week
    if EVENT_COLL in bonus_events:
        comp_gen_data.current_oll_index = (comp_gen_data.current_oll_index + 1) % get_num_COLLs()
        coll_index  = comp_gen_data.current_oll_index
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

    # 1. score previous competition
    # score_competition()

    # 2. post competition to reddit
    reddit_id = post_competition(comp_name, comp_number, event_data, bonus_names, upcoming_bonus_names)

    # 3. save new competition to database
    # save_competition(title, reddit_id, event_data)