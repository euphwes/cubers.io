""" Routes related to displaying competition results. """

from arrow import now

from flask import render_template, redirect
from flask_login import current_user

from app import app
from app.business.user_results import set_medals_on_best_event_results
from app.business.user_results.personal_bests import recalculate_user_pbs_for_event
from app.persistence.comp_manager import get_active_competition, get_complete_competitions,\
    get_previous_competition, get_competition, get_all_comp_events_for_comp, get_comp_event_by_id
from app.persistence.user_results_manager import get_all_complete_user_results_for_comp_event,\
    blacklist_results, unblacklist_results, UserEventResultsDoesNotExistException
from app.util.sorting import sort_user_results_with_rankings
from app.util.events.resources import sort_comp_events_by_global_sort_order

# -------------------------------------------------------------------------------------------------

@app.route('/export/twisty_timer/')
def tt_export():
    """ A route for showing results for a specific competition. """

    pass

