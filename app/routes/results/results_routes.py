""" Routes related to displaying competition results. """

from arrow import utcnow as now
from flask import render_template, redirect

from app import CUBERS_APP
from app.persistence import comp_manager
from app.persistence.models import EventFormat
from app.util.reddit_util import build_times_string

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route('/leaderboards/')
def results_list():
    """ A route for showing which competitions results can be viewed for. """
    comps = comp_manager.get_complete_competitions()
    comp = comp_manager.get_active_competition()
    return render_template("results/results_list.html", comps=comps, active=comp)


@CUBERS_APP.route('/redirect_curr/')
def curr_leaders():
    """ Redirects to the current competition's leaderboards. """
    comp = comp_manager.get_active_competition()
    return redirect("leaderboards/{}".format(comp.id))


@CUBERS_APP.route('/redirect_prev/')
def prev_leaders():
    """ Redirects to the current competition's leaderboards. """
    comp = comp_manager.get_previous_competition()
    return redirect("leaderboards/{}".format(comp.id))


@CUBERS_APP.route('/leaderboards/<int:comp_id>/')
def comp_results(comp_id):
    """ A route for showing results for a specific competition. """

    total_start = now()

    competition = comp_manager.get_competition(comp_id)

    get_comp_start = now()
    comp_events = comp_manager.get_all_comp_events_for_comp(comp_id)
    print("Retrieve comp: " + str(now() - get_comp_start))

    get_all_results_start = now()
    results = comp_manager.get_all_complete_user_results_for_comp(comp_id)
    print("Get all user results for comp " + str(now() - get_all_results_start))

    build_lists_start  = now()
    event_names = [event.Event.name for event in comp_events]
    event_results = {event.Event.name : list() for event in comp_events}
    event_formats = {event.Event.name : event.Event.eventFormat for event in comp_events}
    event_ids     = {event.Event.name : event.Event.id for event in comp_events}
    print("Build lists: " + str(now() - build_lists_start))

    build_times_str_start = now()
    for result in results:
        event_name = result.CompetitionEvent.Event.name
        event_format = event_formats[event_name]

        if event_format == EventFormat.Bo1:
            solves_helper = [result.result]
        else:
            is_fmc = event_name == 'FMC'
            is_blind = event_name in ('2BLD', '3BLD', '4BLD', '5BLD')
            solves_helper = build_times_string(result.solves, event_format, is_fmc, is_blind, want_list=True)

        setattr(result, 'solves_helper', solves_helper)
        event_results[event_name].append(result)
    print("Build time strings: " + str(now() - build_times_str_start))

    # Sort the results
    sort_start = now()
    for event_name, results in event_results.items():
        results.sort(key=cmp_to_key(sort_results))
    print("Sort: " + str(now() - sort_start))


    print("Everything: " + str(now() - total_start))
    return render_template("results/results_comp.html", comp_name=competition.title,\
        event_results=event_results, event_names=event_names, event_formats=event_formats,\
        event_ids=event_ids)


def sort_results(val1, val2):
    result1 = val1.result
    result2 = val2.result
    if not result1:
        result1 = 100000000
    if not result2:
        result2 = 100000000
    if result1 == 'DNF':
        result1 = 99999999
    if result2 == 'DNF':
        result2 = 99999999
    return int(result1) - int(result2)


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
