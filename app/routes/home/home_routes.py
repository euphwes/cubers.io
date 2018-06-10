""" Routes related to the time-entry and competition results pages. """

import json

from flask import render_template, request
from flask_login import current_user

from app import CUBERS_APP
from app.persistence import comp_manager
from app.persistence.user_results_manager import build_user_event_results
from app.util.reddit_util import build_comment_source_from_events_results

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route('/')
def index():
    """ Main page for the app. Shows the competition time entry page if logged in, or an informative
    landing page if not. """
    comp = comp_manager.get_active_competition()
    return render_template('index.html', current_competition = comp)


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

    if current_user.is_authenticated:
        # attempt submit comment
        # if failure, show comment source page with error message
        # if success, show success page with link to comment
        return render_template('times_comment_source.html', comment_source = comment_source)

    # show comment source page
    return render_template('times_comment_source.html', comment_source = comment_source)

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
