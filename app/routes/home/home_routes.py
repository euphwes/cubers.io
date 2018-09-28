""" Routes related to the time-entry and competition results pages. """

import json

from flask import render_template, request, redirect, url_for, abort
from flask_login import current_user

from app import CUBERS_APP
from app.persistence import comp_manager
from app.persistence.models import EventFormat
from app.persistence.user_manager import get_user_by_username
from app.persistence.user_results_manager import build_user_event_results,\
     save_event_results_for_user, get_event_results_for_user
from app.util.reddit_util import build_comment_source_from_events_results,\
     submit_comment_for_user, get_permalink_for_comp_thread, build_times_string,\
     convert_centiseconds_to_friendly_time, update_comment_for_user

# -------------------------------------------------------------------------------------------------

COMMENT_SUCCESS_TEMPLATE = 'submit/comment_submit_success.html'
COMMENT_FAILURE_TEMPLATE = 'submit/comment_submit_failure.html'
COMMENT_SOURCE_TEMPLATE  = 'submit/times_comment_source.html'

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route('/')
def index():
    """ Main page for the app. Shows cards for every event in the current competition."""

    if (not current_user.is_authenticated) and (not 'nologin' in request.args):
        return redirect(url_for(".prompt_login"))

    comp = comp_manager.get_active_competition()

    events_for_json = dict()
    for comp_event in comp.events:
        event = {
            'name':          comp_event.Event.name,
            'scrambles':     list(),
            'event_id':      comp_event.Event.id,
            'comp_event_id': comp_event.id,
            'comment':       '',
        }
        for scram in comp_event.scrambles:
            event['scrambles'].append({
                'id':       scram.id,
                'scramble': scram.scramble,
                'time':     0,
                'isPlusTwo': False,
                'isDNF': False,
            })

        if current_user.is_authenticated:
            event = fill_any_existing_user_data(current_user, event)

        events_for_json[str(comp_event.id)] = event

    ordered_comp_events = list([comp_event for comp_event in comp.events])
    ordered_comp_events.sort(key=lambda c: c.event_id)

    return render_template('index.html', current_competition=comp, events_data=events_for_json,
                           ordered_comp_events=ordered_comp_events)


@CUBERS_APP.route('/prompt_login')
def prompt_login():
    """ Prompts the user to login for the best experience. """
    comp = comp_manager.get_active_competition()
    return render_template('prompt_login/prompt_login.html', current_competition=comp)


@CUBERS_APP.route('/save_event', methods=['POST'])
def save_event():
    """ A route for saving a specific event to the database. """

    if not current_user.is_authenticated:
        return abort(400, "authenticated users only")

    try:
        user_events  = request.get_json()
        event_result = build_user_results(user_events)[0]
        user = get_user_by_username(current_user.username)
        save_event_results_for_user(event_result, user)
        return ('', 204) # intentionally empty, 204 No Content

    except Exception as ex:
        return abort(500, str(ex))


@CUBERS_APP.route('/submit', methods=['POST'])
def submit_times():
    """ A route for submitting user times for a competition. If the user is authenticated, save
    the times to the database as an intermediate step. Generate source for a /r/cubers comp
    thread comment. If the user is authenticated, submit the comment for them, or else
    redirect to a page where the comment source is displayed. """

    #TODO Clean this garbage up, my god

    #TODO Figure out how to handle it if authenticated user is only submitting incomplete events
    # nothing to submit to reddit, but still need to save to database

    data = request.form['input-results']

    user_events    = json.loads(data)
    user_results   = build_user_results(user_events)
    comment_source = build_comment_source_from_events_results(user_results)

    comp = comp_manager.get_active_competition()
    comp_reddit_id = comp.reddit_thread_id
    comp_thread_url = get_permalink_for_comp_thread(comp_reddit_id)

    for results in user_results:
        if results.is_complete():
            any_complete_to_post = True
            break

    if current_user.is_authenticated:
        user = get_user_by_username(current_user.username)

        is_resubmit = False
        old_reddit_comment_id = None
        for result in user_results:
            prev_result = get_event_results_for_user(result.comp_event_id, user)
            if prev_result:
                is_resubmit = True
                old_reddit_comment_id = prev_result.reddit_comment
                break

        try:
            if not is_resubmit:
                url, comment_id = submit_comment_for_user(user, comp_reddit_id, comment_source)
                for result in user_results:
                    result.reddit_comment = comment_id
                    save_event_results_for_user(result, user)
            else:
                url, comment_id = update_comment_for_user(user, old_reddit_comment_id, comment_source)
                for result in user_results:
                    result.reddit_comment = comment_id
                    save_event_results_for_user(result, user)
            return render_template(COMMENT_SUCCESS_TEMPLATE, comment_url=url,
                                   current_competition=comp)
        except Exception as e:
            return render_template(COMMENT_FAILURE_TEMPLATE, comment_source=comment_source,
                                   comp_url=comp_thread_url, current_competition=comp)

    # show comment source page
    return render_template(COMMENT_SOURCE_TEMPLATE, comment_source=comment_source,
                           comp_url=comp_thread_url, current_competition=comp)


@CUBERS_APP.route('/eventSummaries', methods=['POST'])
def get_event_summaries():
    """ A route for building a time list/summary for an event. TODO: fill out more here. """

    data = request.get_json()

    build_results = build_user_event_results
    friendly = convert_centiseconds_to_friendly_time

    summaries = dict()
    for event in data:
        results = build_results(event['comp_event_id'], event['scrambles'], event['comment'])
        event_format = comp_manager.get_event_by_name(event['name']).eventFormat
        is_fmc = event['name'] == 'FMC'

        if event_format == EventFormat.Bo1:
            summary = friendly(results.single)

        else:
            best = results.single if (event_format == EventFormat.Bo3) else results.average
            if not is_fmc:
                best = friendly(best)
            else:
                best = (best/100)
                if best == int(best):
                    best = int(best)

            times_string = build_times_string(results.solves, event_format, is_fmc)
            summary = "{} = {}".format(best, times_string)

        summaries[event['comp_event_id']] = summary

    return json.dumps(summaries)

# -------------------------------------------------------------------------------------------------

def build_user_results(user_events):
    """ docstring here """

    user_results = list()

    for comp_event_id, solves_dict in user_events.items():
        solves = solves_dict['scrambles']
        comment = solves_dict.get('comment', '')
        event_results = build_user_event_results(comp_event_id, solves, comment)
        if event_results:
            user_results.append(event_results)

    return user_results


def fill_any_existing_user_data(curr_user, event):
    """ asd """
    user = get_user_by_username(curr_user.username)
    prev = get_event_results_for_user(event['comp_event_id'], user)
    if not prev:
        event['save_status'] = 'new'
        return event

    event['save_status'] = 'saved'
    event['comment'] = prev.comment
    for solve in prev.solves:
        scramble_id = solve.scramble_id
        for scram in event['scrambles']:
            if scram['id'] != scramble_id:
                continue
            scram['time'] = solve.time
            scram['isPlusTwo'] = solve.is_plus_two
            scram['isDNF'] = solve.is_dnf

    return event
