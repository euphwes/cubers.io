""" Routes related to displaying competition results. """

from flask import render_template, redirect
from flask_login import current_user

from app import CUBERS_APP
from app.business.user_results import recalculate_user_pbs_for_event
from app.business.rankings import precalculate_site_rankings_for_event
from app.persistence.comp_manager import get_active_competition, get_complete_competitions,\
    get_previous_competition, get_competition, get_all_comp_events_for_comp
from app.persistence.user_results_manager import get_all_complete_user_results_for_comp,\
    blacklist_results, unblacklist_results, UserEventResultsDoesNotExistException

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route('/results/blacklist/<int:results_id>/')
def blacklist(results_id):
    """ Blacklists the specified UserEventResults. """

    if not (current_user.is_authenticated and current_user.is_admin):
        return ("Hey, you're not allowed to do that.", 403)

    # pylint: disable=W0703
    try:
        note = "Manually blacklisted by {}".format(current_user.username)
        results = blacklist_results(results_id, note)

        # Recalculate PBs just for the affected user and event
        recalculate_user_pbs_for_event(results.user_id, results.CompetitionEvent.event_id)

        # Blacklisting a result will bump this person down in the ranks, meaning other people will
        # rise in the ranks. Recalculate UserSiteRankings for all users, just for this event
        precalculate_site_rankings_for_event(results.CompetitionEvent.Event)

        return ('', 204)

    except UserEventResultsDoesNotExistException as ex:
        return (str(ex), 500)

    except Exception as ex:
        return (str(ex), 500)


@CUBERS_APP.route('/results/unblacklist/<int:results_id>/')
def unblacklist(results_id):
    """ Unblacklists the specified UserEventResults. """

    if not (current_user.is_authenticated and current_user.is_admin):
        return ("Hey, you're not allowed to do that.", 403)

    # pylint: disable=W0703
    try:
        results = unblacklist_results(results_id)

        # Recalculate PBs just for the affected user and event
        recalculate_user_pbs_for_event(results.user_id, results.CompetitionEvent.event_id)

        # Unlacklisting a result will bump this person up in the ranks, meaning other people will
        # fall in the ranks. Recalculate UserSiteRankings for all users, just for this event
        precalculate_site_rankings_for_event(results.CompetitionEvent.Event)

        return ('', 204)

    except UserEventResultsDoesNotExistException as ex:
        return (str(ex), 500)

    except Exception as ex:
        return (str(ex), 500)

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route('/leaderboards/')
def results_list():
    """ A route for showing which competitions results can be viewed for. """

    comps = get_complete_competitions()
    comp = get_active_competition()
    return render_template("results/results_list.html", comps=comps, active=comp)


@CUBERS_APP.route('/redirect_curr/')
def curr_leaders():
    """ Redirects to the current competition's leaderboards. """

    comp = get_active_competition()
    return redirect("leaderboards/{}".format(comp.id))


@CUBERS_APP.route('/redirect_prev/')
def prev_leaders():
    """ Redirects to the current competition's leaderboards. """

    comp = get_previous_competition()
    return redirect("leaderboards/{}".format(comp.id))


@CUBERS_APP.route('/leaderboards/<int:comp_id>/')
def comp_results(comp_id):
    """ A route for showing results for a specific competition. """

    competition = get_competition(comp_id)
    if not competition:
        return "Oops, that's not a real competition. Try again, ya clown."

    comp_events = get_all_comp_events_for_comp(comp_id)

    # If the page is being viewed by an admin, include blacklisted results and set `show_admin`
    # flag so we render the controls for toggling blacklist status
    if current_user.is_authenticated and current_user.is_admin:
        print('Admin {} viewing page, setting show_admin=True'.format(current_user.username))
        show_admin = True
        results = get_all_complete_user_results_for_comp(comp_id, omit_blacklisted=False)

    # Otherwise this is being viewed by a normal user, omit blacklisted results like normal
    # and don't set the `show_admin` flag
    else:
        show_admin = False
        results = get_all_complete_user_results_for_comp(comp_id)

    event_names   = [event.Event.name for event in comp_events]
    event_results = {event.Event.name : list() for event in comp_events}
    event_formats = {event.Event.name : event.Event.eventFormat for event in comp_events}
    event_ids     = {event.Event.name : event.Event.id for event in comp_events}

    for result in results:
        event_name = result.CompetitionEvent.Event.name
        solves_helper = result.times_string.split(', ')
        while len(solves_helper) < 5:
            solves_helper.append('')
        setattr(result, 'solves_helper', solves_helper)
        event_results[event_name].append(result)

    # Sort the results
    for event_name, results in event_results.items():
        results.sort(key=cmp_to_key(sort_results))

    alternative_title = "{} leaderboards".format(competition.title)

    return render_template("results/results_comp.html", alternative_title=alternative_title,\
        event_results=event_results, event_names=event_names, event_formats=event_formats,\
        event_ids=event_ids, show_admin=show_admin)

# TODO: put the UserEventResults sorting stuff somewhere else

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
