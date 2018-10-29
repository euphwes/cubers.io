""" Routes related to displaying competition results. """

import json

from flask import request, abort, render_template
from flask_login import current_user

from app import CUBERS_APP
from app.persistence import comp_manager
from app.persistence.models import EventFormat
from app.persistence.user_manager import get_user_by_username
from app.persistence.user_results_manager import build_user_event_results,\
    save_event_results_for_user, build_all_user_results
from app.util.reddit_util import build_times_string, convert_centiseconds_to_friendly_time,\
    get_permalink_for_comp_thread

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route('/results')
def results_list():
    """ A route for showing which competitions results can be viewed for. """

    comps = comp_manager.get_complete_competitions()
    comp = comp_manager.get_active_competition()

    updated_comps = list()
    for comp in comps:
        updated_comp = ['','','','']
        updated_comp[0] = comp[0]
        updated_comp[1] = comp[1]
        updated_comp[2] = comp[2]
        updated_comp[3] = get_permalink_for_comp_thread(comp[3])
        #
        updated_comps.append(updated_comp)

    return render_template("results/results_list.html", comps=updated_comps, current_competition=comp)
