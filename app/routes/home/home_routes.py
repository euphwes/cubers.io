""" Routes related to the time-entry and competition results pages. """

import json

from flask import render_template, abort, request
from flask_login import current_user

from app import CUBERS_APP
from app.persistence import comp_manager

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

    if current_user.is_authenticated:
        return handle_user_submit_times(user_events)

    else:
        return ""
        #return handle_anon_submit_times(user_events)


@CUBERS_APP.route('/comp/<competition_id>')
def competition(competition_id):
    try:
        competition_id = int(competition_id)
    except ValueError:
        # TODO: come up with custom 404 not found page
        return abort(404)

    return render_template('comp.html', competition = comp_manager.get_competition(competition_id))


# -------------------------------------------------------------------------------------------------

def handle_user_submit_times(user_events):
    """ docstring here """

    return ""

    for comp_event_id, solves in user_events.items():
        a = 1