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
from app.util.sorting import sort_user_event_results
from app.util.events.resources import sort_comp_events_by_global_sort_order

# -------------------------------------------------------------------------------------------------

DEFAULT_BLACKLIST_NOTE = 'Results manually hidden by {username} on {date}.'

LOG_ADMIN_BLACKLISTED = '{} blacklisted results {}'
LOG_ADMIN_UNBLACKLISTED = '{} unlacklisted results {}'
LOG_USER_VIEWING_RESULTS = '{} viewing results for {} in {}'

# -------------------------------------------------------------------------------------------------

@app.route('/leaderboards/<int:comp_id>/')
def comp_results(comp_id):
    """ A route for showing results for a specific competition. """

    competition = get_competition(comp_id)
    if not competition:
        return "Oops, that's not a real competition. Try again, ya clown."

    comp_events = get_all_comp_events_for_comp(comp_id)
    comp_events = sort_comp_events_by_global_sort_order(comp_events)

    events_names_ids = list()
    id_3x3 = None
    for comp_event in comp_events:
        if comp_event.Event.name == '3x3':
            id_3x3 = comp_event.id
        events_names_ids.append({
            'name':          comp_event.Event.name,
            'comp_event_id': comp_event.id,
            'event_id':      comp_event.Event.id,
        })

    alternative_title = "{} leaderboards".format(competition.title)

    return render_template("results/results_comp.html", alternative_title=alternative_title,
        events_names_ids=events_names_ids, id_3x3=id_3x3, comp_id=comp_id)


@app.route('/compevent/<comp_event_id>/')
def comp_event_results(comp_event_id):
    """ A route for obtaining results for a specific competition event and rendering them
    for the leaderboards pages. """

    if 'overall' in comp_event_id:
        return get_overall_performance_data(int(comp_event_id.replace('overall_', '')))

    comp_event_id = int(comp_event_id)

    comp_event = get_comp_event_by_id(comp_event_id)

    # If the page is being viewed by an admin, render the controls for toggling blacklist status
    # and also apply additional styling on blacklisted results to make them easier to see
    show_admin = current_user.is_admin

    log_msg = LOG_USER_VIEWING_RESULTS.format(current_user.username, comp_event.Event.name,
                                              comp_event.Competition.title)
    app.logger.info(log_msg, extra={'is_admin': show_admin})

    # Store the scrambles so we can show those too
    scrambles = [s.scramble for s in comp_event.scrambles]

    results = get_all_complete_user_results_for_comp_event(comp_event_id, omit_blacklisted=False)
    results = list(results)  # take out of the SQLAlchemy BaseQuery and put into a simple list

    if not results:
        return "Nobody has participated in this event yet. Maybe you'll be the first!"

    results = filter_blacklisted_results(results, show_admin, current_user)

    # Split the times string into components, add to a list called `"solves_helper` which
    # is used in the UI to show individual solves, and make sure the length == 5, filled
    # with empty strings if necessary
    # TODO put this in business logic somewhere
    for result in results:
        solves_helper = result.times_string.split(', ')
        while len(solves_helper) < 5:
            solves_helper.append('')
        setattr(result, 'solves_helper', solves_helper)

    # Sort the results
    results.sort(key=sort_user_event_results)

    return render_template("results/comp_event_table.html", results=results,
        comp_event=comp_event, show_admin=show_admin, scrambles=scrambles)


def get_overall_performance_data(comp_id):
    """ TODO: comment """

    user_points = dict()

    for comp_event in get_all_comp_events_for_comp(comp_id):
        results = get_all_complete_user_results_for_comp_event(comp_event.id)
        results = list(results)
        results.sort(key=sort_user_event_results)

        total_participants = len(results)
        for i, result in enumerate(results):
            username = result.User.username
            if username not in user_points.keys():
                user_points[username] = 0
            user_points[username] += (total_participants - i)

    user_points = [(username, points) for username, points in user_points.items()]
    user_points.sort(key=lambda x: x[1], reverse=True)

    if not user_points:
        return "Nobody has participated in anything yet this week?"

    return render_template("results/overall_points.html", user_points=user_points)

# -------------------------------------------------------------------------------------------------

@app.route('/redirect_curr/')
def curr_leaders():
    """ Redirects to the current competition's leaderboards. """

    comp = get_active_competition()
    return redirect("leaderboards/{}".format(comp.id))


@app.route('/redirect_prev/')
def prev_leaders():
    """ Redirects to the current competition's leaderboards. """

    comp = get_previous_competition()
    return redirect("leaderboards/{}".format(comp.id))


@app.route('/leaderboards/')
def results_list():
    """ A route for showing which competitions results can be viewed for. """

    comps = get_complete_competitions()
    comp = get_active_competition()
    return render_template("results/results_list.html", comps=comps, active=comp)

# -------------------------------------------------------------------------------------------------

@app.route('/results/blacklist/<int:results_id>/')
def blacklist(results_id):
    """ Blacklists the specified UserEventResults. """

    if not (current_user.is_authenticated and current_user.is_admin):
        return ("Hey, you're not allowed to do that.", 403)

    # pylint: disable=W0703
    try:
        actor = current_user.username
        timestamp = now().format('YYYY-MM-DD')
        note = DEFAULT_BLACKLIST_NOTE.format(username=actor, date=timestamp)
        results = blacklist_results(results_id, note)

        app.logger.info(LOG_ADMIN_BLACKLISTED.format(current_user.username, results.id))

        # Recalculate PBs just for the affected user and event
        recalculate_user_pbs_for_event(results.user_id, results.CompetitionEvent.event_id)

        # Recalculate podiums for this comp and event if the competition isn't active
        if not results.CompetitionEvent.Competition.active:
            set_medals_on_best_event_results([results.CompetitionEvent])

        return ('', 204)

    except UserEventResultsDoesNotExistException as ex:
        app.logger.error(str(ex))
        return (str(ex), 500)

    except Exception as ex:
        app.logger.error(str(ex))
        return (str(ex), 500)


@app.route('/results/unblacklist/<int:results_id>/')
def unblacklist(results_id):
    """ Unblacklists the specified UserEventResults. """

    if not (current_user.is_authenticated and current_user.is_admin):
        return ("Hey, you're not allowed to do that.", 403)

    # pylint: disable=W0703
    try:
        results = unblacklist_results(results_id)
        app.logger.info(LOG_ADMIN_UNBLACKLISTED.format(current_user.username, results.id))

        # Recalculate PBs just for the affected user and event
        recalculate_user_pbs_for_event(results.user_id, results.CompetitionEvent.event_id)

        # Recalculate podiums for this comp and event if the competition isn't active
        if not results.CompetitionEvent.Competition.active:
            set_medals_on_best_event_results([results.CompetitionEvent])

        return ('', 204)

    except UserEventResultsDoesNotExistException as ex:
        app.logger.error(str(ex))
        return (str(ex), 500)

    except Exception as ex:
        app.logger.error(str(ex))
        return (str(ex), 500)

# -------------------------------------------------------------------------------------------------

def filter_blacklisted_results(results, show_admin, curr_user):
    """ Filters out the appropriate blacklisted results depending on who is viewing the page.
    Admins see all results, non-logged viewers see no blacklisted results, and logged-in viewers
    only see their own. """

    if show_admin:
        return results

    if not curr_user.is_authenticated:
        return [r for r in results if not r.is_blacklisted]

    target_username = curr_user.username
    return [r for r in results if (not r.is_blacklisted) or (r.User.username == target_username)]
