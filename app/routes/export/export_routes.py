""" Routes related to displaying competition results. """

from flask import request, Response
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
    """ Exports a user's solves to a format that can be imported into TwistyTimer. """

    # Maps the cubers.io event name to a puzzle/category that will be recognized by TwistyTimer
    # Not all cubers.io events will be exported to TwistyTimer, since there's not really a
    # reasonable place to put them. For example, it makes sense to make Kilominx a category
    # of Megaminx, but what regular event would Redi Cube be a category of? What about relays? etc
    event_name_to_category_map = {
        # NxN
        '2x2': ['222', 'Normal'],
        '3x3': ['333', 'Normal'],
        '4x4': ['444', 'Normal'],
        '5x5': ['555', 'Normal'],
        '6x6': ['666', 'Normal'],
        '7x7': ['777', 'Normal'],

        # Other WCA events
        'Square-1': ['sq1', 'Normal'],
        'Clock':    ['clock', 'Normal'],
        'Pyraminx': ['pyra', 'Normal'],
        'Megaminx': ['mega', 'Normal'],
        'Skewb':    ['skewb', 'Normal'],

        # 3x3 variants
        '3BLD':                   ['333', '3BLD'],
        'LSE':                    ['333', 'LSE'],
        'F2L':                    ['333', 'F2L'],
        '2GEN':                   ['333', '2-GEN'],
        '3x3OH':                  ['333', 'OH'],
        'Void Cube':              ['333', 'Void Cube'],
        '3x3 With Feet':          ['333', 'With Feet'],
        '3x3 Mirror Blocks/Bump': ['333', 'Mirror Blocks'],

        # Other NxN variants
        '2BLD':     ['222', '2BLD'],
        '4BLD':     ['444', '4BLD'],
        '4x4 OH':   ['444', 'OH'],
        '5BLD':     ['555', '5BLD'],
        'Kilominx': ['mega', 'Kilominx']
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
