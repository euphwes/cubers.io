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

@CUBERS_APP.route('/results/')
def results_list():
    """ A route for showing which competitions results can be viewed for. """
    comps = comp_manager.get_complete_competitions()
    comp = comp_manager.get_active_competition()
    return render_template("results/results_list.html", comps=comps, active=comp)


@CUBERS_APP.route('/results/<int:comp_id>/')
def comp_results(comp_id):
    """ A route for showing results for a specific competition. """

    results = comp_manager.get_all_user_results_for_comp(comp_id)
    comp_events = comp_manager.get_all_comp_events_for_comp(comp_id)
    event_names = [event.Event.name for event in comp_events]
    event_results = {event.Event.name : list() for event in comp_events}

    for result in results:
        event_name = result.CompetitionEvent.Event.name
        event_results[event_name].append(result)

    for event_name, results in event_results.items():
        results.sort(key=cmp_to_key(sort_results_average))
        results.sort(key=cmp_to_key(sort_results_single))

    comps = comp_manager.get_complete_competitions()
    comp = comp_manager.get_active_competition()

    return render_template("results/results_comp.html", event_results=event_results, event_names=event_names)

def sort_results_average(val1, val2):
    if val1.average == 'PENDING' and val2.average == 'PENDING':
        return 0
    if val1.average == 'PENDING':
        return -1
    if val2.average == 'PENDING':
        return 1
    return int(val1.average) - int(val2.average)

def sort_results_single(val1, val2):
    if val1.single == 'PENDING' and val2.single == 'PENDING':
        return 0
    if val1.single == 'PENDING':
        return -1
    if val2.single == 'PENDING':
        return 1
    return int(val1.single) - int(val2.single)

def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class comparator:
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return comparator