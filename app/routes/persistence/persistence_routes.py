""" Routes related to saving results to the database. """

import traceback
import json

from http import HTTPStatus

from flask import request, abort
from flask_login import current_user

from app import app
from app.business.user_results.creation import process_event_results
from app.persistence.models import UserSolve, UserEventResults
from app.persistence.comp_manager import get_comp_event_by_id
from app.persistence.user_results_manager import save_event_results, get_event_results_for_user

# -------------------------------------------------------------------------------------------------

LOG_EVENT_RESULTS_TEMPLATE = "{}: submitted {} results"
LOG_RESULTS_ERROR_TEMPLATE = "{}: error creating or saving {} results"
LOG_SAVED_RESULTS_TEMPLATE = "{}: saved {} results"

# Solve data dictionary keys
IS_DNF        = 'is_dnf'
IS_PLUS_TWO   = 'is_plus_two'
SCRAMBLE_ID   = 'scramble_id'
COMP_EVENT_ID = 'comp_event_id'
CENTISECONDS  = 'elapsed_centiseconds'
EXPECTED_FIELDS = (IS_DNF, IS_PLUS_TWO, SCRAMBLE_ID, COMP_EVENT_ID, CENTISECONDS)

# -------------------------------------------------------------------------------------------------

@app.route('/post_solve', methods=['POST'])
def post_solve():
    """ TODO: make this better, saves a solve """

    if not current_user.is_authenticated:
        app.logger.warning('unauthenticated user attempting save_event')
        return abort(HTTPStatus.UNAUTHORIZED)

    # Extract JSON solve data, deserialize to dictionary, and verify that all expected fields are present
    solve_data = json.loads(request.data)
    if not all(key in solve_data for key in EXPECTED_FIELDS):
        return ('oops you forgot some data', HTTPStatus.BAD_REQUEST)

    # Extract all the specific fields out of the solve data dictionary
    is_dnf        = solve_data[IS_DNF]
    is_plus_two   = solve_data[IS_PLUS_TWO]
    scramble_id   = solve_data[SCRAMBLE_ID]
    comp_event_id = solve_data[COMP_EVENT_ID]
    centiseconds  = solve_data[CENTISECONDS]

    # Retrieve the specified competition event
    comp_event = get_comp_event_by_id(comp_event_id)
    if not comp_event:
        return ("Can't find that event, oops.", HTTPStatus.NOT_FOUND)

    # Verify that the competition event belongs to the active competition. If it doesn't, return an error message
    comp = comp_event.Competition
    if not comp.active:
        return ("Oops, that event belongs to a competition which has ended.", HTTPStatus.BAD_REQUEST)

    # Retrieve the user's results record for this event, if they exist, or else create a new record
    user_event_results = get_event_results_for_user(comp_event_id, current_user)
    if not user_event_results:
        user_event_results = UserEventResults(comp_event_id=comp_event_id, user_id=current_user.id)

    solve = UserSolve(time=centiseconds, is_dnf=is_dnf, is_plus_two=is_plus_two, scramble_id=scramble_id)
    user_event_results.solves.append(solve)

    process_event_results(user_event_results, comp_event, current_user)

    save_event_results(user_event_results)

    return ('', HTTPStatus.NO_CONTENT)

# -------------------------------------------------------------------------------------------------

def __create_results_log_context(user, event_name, event_result: UserEventResults):
    """ Builds some logging context related to creating/updating user events results. """

    results_info = event_result.to_log_dict()
    results_info['event_name'] = event_name

    return {
        'username': user.username,
        'results': results_info
    }


def __create_results_error_log_context(user, ex):
    """ Builds some logging context related to errors during creating/updating user events results. """

    return {
        'username': user.username,
        'exception': {
            'message': str(ex),
            'stack': traceback.format_exc()
        },
    }
