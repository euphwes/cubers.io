""" Routes related to displaying competition results. """

from arrow import now

from flask import render_template, redirect, request, Response
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
from app.routes import api_login_required

# -------------------------------------------------------------------------------------------------

class TwistyTimerResultsExporter:
    """ Exports a user's cubers.io solves to a format that can be imported into TwistyTimer. """

    event_name_to_category_map = {
        '3x3': ['333', 'Normal'],
    }

    def __init__(self, username, event_name_results_map):
        self.event_name_results_map = event_name_results_map
        self.username = username

    def generate_results(self):
        """ Returns a generator (TODO is this right?) which yield TwistyTimer-flavor CSV lines
        containing the user's solve info. """

        def gen_results():
            yield '1'
            yield '2'
            yield "3"

        return gen_results()

# -------------------------------------------------------------------------------------------------

@app.route('/api/export')
@api_login_required
def export():
    """ A route for exporting a user's results. """

    return Response(TwistyTimerResultsExporter(None, None).generate_results(), mimetype="text/plain",
            headers={"Content-Disposition": "attachment;filename=test.txt"})
