""" API routes for submitting results for competitions, and for posting new competitions. """

import json

from flask import render_template, request
from flask_login import current_user

from app import CUBERS_APP
from app.persistence import comp_manager
from app.persistence.models import EventFormat
from app.persistence.user_manager import get_user_by_username
from app.persistence.user_results_manager import build_user_event_results,\
     save_event_results_for_user, get_event_results_for_user_and_comp_event
from app.util.reddit_util import build_comment_source_from_events_results,\
     submit_comment_for_user, get_permalink_for_comp_thread, build_times_string,\
     convert_centiseconds_to_friendly_time, update_comment_for_user

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route('/getCurrentCompetition', methods=['GET'])
def get_competition():
    """ Retrieve the current competition data. """
    pass


@CUBERS_APP.route('/createNewCompetition', methods=['POST'])
def new_competition():
    """ Create a new competition based on the data coming in. """
    pass
