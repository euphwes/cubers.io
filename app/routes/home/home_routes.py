""" Routes related to the time-entry and competition results pages. """

import json

from flask import render_template, request
from flask_login import current_user

from app import CUBERS_APP
from app.persistence import comp_manager
from app.persistence.user_results_manager import build_user_event_results
from app.util.reddit_util import build_comment_source_from_events_results,\
     submit_comment_for_user, get_permalink_for_comp_thread, build_times_string,\
     convert_centiseconds_to_friendly_time

# -------------------------------------------------------------------------------------------------

COMMENT_SUCCESS_TEMPLATE = 'comment_submit_success.html'
COMMENT_FAILURE_TEMPLATE = 'comment_submit_failure.html'
COMMENT_SOURCE_TEMPLATE  = 'times_comment_source.html'

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route('/')
def index():
    """ Main page for the app. Shows the competition time entry page if logged in, or an informative
    landing page if not. """
    comp = comp_manager.get_active_competition()

    events_data = dict()
    for comp_event in comp.events:
        event = {
            'name':          comp_event.Event.name,
            'scrambles':     list(),
            'event_id':      comp_event.Event.id,
            'comp_event_id': comp_event.id,
        }
        for scram in comp_event.scrambles:
            event['scrambles'].append({
                'id':       scram.id,
                'scramble': scram.scramble
            })
        events_data[str(comp_event.id)] = event

    return render_template('index.html', current_competition=comp, events_data=events_data)


@CUBERS_APP.route('/submit', methods=['POST'])
def submit_times():
    """ A route for submitting user times for a competition. If the user is authenticated, save
    the times to the database as an intermediate step. Generate source for a /r/cubers comp
    thread comment. If the user is authenticated, submit the comment for them, or else
    redirect to a page where the comment source is displayed. """

    data = request.form['input-results']

    user_events    = json.loads(data)
    user_results   = build_user_results(user_events)
    comment_source = build_comment_source_from_events_results(user_results)

    comp_reddit_id = comp_manager.get_active_competition().reddit_thread_id
    comp_thread_url = get_permalink_for_comp_thread(comp_reddit_id)

    if current_user.is_authenticated:
        try:
            url = submit_comment_for_user(current_user.username, comp_reddit_id, comment_source)
            return render_template(COMMENT_SUCCESS_TEMPLATE, comment_url=url)
        except:
            # TODO figure out what PRAW can actually throw here
            return render_template(COMMENT_FAILURE_TEMPLATE, comment_source=comment_source,
                                   comp_url=comp_thread_url)

    # show comment source page
    return render_template(COMMENT_SOURCE_TEMPLATE, comment_source=comment_source, comp_url=comp_thread_url)


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

        best = friendly(results.average) if (event_format != 'Bo3') else friendly(results.single)
        times_string = build_times_string(results.solves, event_format)

        summaries[event['comp_event_id']] = "{} = {}".format(best, times_string)

    return json.dumps(summaries)

# -------------------------------------------------------------------------------------------------

def build_user_results(user_events):
    """ docstring here """

    user_results = list()
    for comp_event_id, solve_comment_dict in user_events.items():
        solves = solve_comment_dict['scrambles']
        comment = solve_comment_dict['comment']
        event_results = build_user_event_results(comp_event_id, solves, comment)
        user_results.append(event_results)

    return user_results
