""" Logic for creating a new competition based on the last one. """

from app.persistence.comp_manager import get_competition_gen_resources,\
save_competition_gen_resources, create_new_competition

from scripts.events_resources import get_WCA_events, get_non_WCA_events,\
get_bonus_events_rotation_starting_at, get_COLL_at_index, get_bonus_events_without_current,\
get_num_COLLs, get_num_bonus_events, EVENT_COLL

# -------------------------------------------------------------------------------------------------

BONUS_EVENT_COUNT = 5
COMPETITION_NAME_TEMPLATE = 'Cubing Competition {}!'

# -------------------------------------------------------------------------------------------------

def generate_new_competition():
    """ Generate a new competition object based on the previous one. """

    # Get the info required to know what events and COLL to do next
    comp_gen_data = get_competition_gen_resources()

    # Figure out next competition number and name
    comp_number = comp_gen_data.current_comp_num + 1
    competition_name = COMPETITION_NAME_TEMPLATE.format(comp_number)

    # Generate scrambles for every WCA event
    event_data = []
    for wca_event in get_WCA_events():
        event_data.append(dict({
            'event':     wca_event,
            'name':      wca_event.name,
            'scrambles': wca_event.get_scrambles()
        }))

    # Get the next COLL index and number
    coll_index   = (comp_gen_data.current_oll_index + 1) % get_num_COLLs()
    coll_number = get_COLL_at_index(coll_index)

    bonus_index = (comp_gen_data.current_bonus_index + BONUS_EVENT_COUNT) % get_num_bonus_events()
    bonus_events = get_bonus_events_rotation_starting_at(bonus_index, BONUS_EVENT_COUNT)

    # Generate scrambles for the bonus events in this comp
    for bonus_event in bonus_events:
        if bonus_event == EVENT_COLL:
            scrambles = bonus_event.get_scrambles(coll_number)
        else:
            scrambles = bonus_event.get_scrambles()
        event_data.append(dict({
            'event':     bonus_event,
            'name':      bonus_event.name,
            'scrambles': scrambles
        }))

    #competition_post = post_comp_to_reddit(competition_name, event_data)