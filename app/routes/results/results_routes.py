""" Routes related to displaying competition results. """

from flask import render_template, redirect
from flask_login import current_user

from app import CUBERS_APP
from app.persistence import comp_manager
from app.persistence.user_manager import get_blacklisted_users_for_competition

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

    competition = comp_manager.get_competition(comp_id)
    if not competition:
        # TODO: do this right, with a neat 404 or something
        return "Oops, that's not a real competition. Try again, ya clown."

    blacklisted_users = get_blacklisted_users_for_competition(comp_id)

    comp_events = comp_manager.get_all_comp_events_for_comp(comp_id)

    results = comp_manager.get_all_complete_user_results_for_comp(comp_id)

    event_names   = [event.Event.name for event in comp_events]
    event_results = {event.Event.name : list() for event in comp_events}
    event_formats = {event.Event.name : event.Event.eventFormat for event in comp_events}
    event_ids     = {event.Event.name : event.Event.id for event in comp_events}

    for result in results:
        # Skip results for users that are in the blacklist, unless it's the current user
        # This way blacklisted users will see their own results, but others won't
        if (result.User in blacklisted_users) and (result.User != current_user):
            continue
        event_name = result.CompetitionEvent.Event.name
        solves_helper = result.times_string.split(', ')
        setattr(result, 'solves_helper', solves_helper)
        event_results[event_name].append(result)

    # Sort the results
    for event_name, results in event_results.items():
        results.sort(key=cmp_to_key(sort_results))

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
