""" Business logic for aggregating a user's history across the competitions. """

from collections import OrderedDict

from app.persistence.comp_manager import get_all_events_user_has_participated_in,\
    get_all_competitions_user_has_participated_in
from app.persistence.user_results_manager import get_all_complete_user_results_for_comp_and_user

# -------------------------------------------------------------------------------------------------

def get_user_competition_history(user):
    """ Returns user competition history in the following format:
    dict[Event][dict[Competition][UserEventResults]] """

    history = OrderedDict()
    id_to_events = dict()

    all_events = get_all_events_user_has_participated_in(user.id)

    # Iterate over all competitions checking for results for this user. Reverse the order of
    # the comps so they are displayed in the user profile page with most recent comps first
    all_comps = get_all_competitions_user_has_participated_in(user.id)
    all_comps.reverse()

    # Prepare a results history in the master history for each event the user has participated in
    for event in all_events:
        history[event] = OrderedDict()
        id_to_events[event.id] = event

    for comp in all_comps:
        for results in get_all_complete_user_results_for_comp_and_user(comp.id, user.id):
            event = id_to_events[results.CompetitionEvent.event_id]

            # Doesn't make sense to keep COLL records, since it's a single alg that changes weekly
            if event.name == "COLL":
                continue

            # Split the times string into components, add to a list called `"solves_helper` which
            # is used in the UI to show individual solves, and make sure the length == 5, filled
            # with empty strings if necessary
            solves_helper = results.times_string.split(', ')
            while len(solves_helper) < 5:
                solves_helper.append('')
            setattr(results, 'solves_helper', solves_helper)

            # Store these UserEventResults for this Competition
            history[event][comp] = results

    return history
