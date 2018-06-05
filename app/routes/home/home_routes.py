""" Routes related to the time-entry and competition results pages. """

import json

from flask import render_template, abort, request
from flask_login import current_user

from app import CUBERS_APP
from app.persistence import comp_manager, user_results_manager

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

    user_events = json.loads(request.get_data().decode('utf-8'))
    user_results = build_user_results(user_events)

    if current_user.is_authenticated:
        # attempt submit comment, if failure, show comment source page with no error message
        return user_results

    else:
        # redirect to comment source page
        return ""

# -------------------------------------------------------------------------------------------------

def build_user_results(user_events):
    """ docstring here """

    user_results = list()
    for comp_event_id, solves in user_events.items():
        event_results = user_results_manager.build_user_event_results(comp_event_id, solves)
        user_results.append(event_results)

    return user_events
