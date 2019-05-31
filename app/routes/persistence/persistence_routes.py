""" Routes related to saving results to the database. """

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

ERR_MSG_MISSING_INFO = 'Some required information is missing from your solve.'
ERR_MSG_NO_SUCH_EVENT = "Can't find a competition event with ID {}."
ERR_MSG_INACTIVE_COMP = 'This event belongs to a competition which has ended.'

# -------------------------------------------------------------------------------------------------

@app.route('/post_solve', methods=['POST'])
def post_solve():
    """ Saves a solve. Ensures the user has UserEventResults for this event, associated this solve
    with those results, and processes the results to make sure all relevant data is up-to-date. """

    if not current_user.is_authenticated:
        return abort(HTTPStatus.UNAUTHORIZED)

    # Extract JSON solve data, deserialize to dict, and verify that all expected fields are present
    solve_data = json.loads(request.data)
    if not all(key in solve_data for key in EXPECTED_FIELDS):
        return (ERR_MSG_MISSING_INFO, HTTPStatus.BAD_REQUEST)

    # Extract all the specific fields out of the solve data dictionary
    is_dnf        = solve_data[IS_DNF]
    is_plus_two   = solve_data[IS_PLUS_TWO]
    scramble_id   = solve_data[SCRAMBLE_ID]
    comp_event_id = solve_data[COMP_EVENT_ID]
    centiseconds  = solve_data[CENTISECONDS]

    # Retrieve the specified competition event
    comp_event = get_comp_event_by_id(comp_event_id)
    if not comp_event:
        return (ERR_MSG_NO_SUCH_EVENT.format(comp_event_id), HTTPStatus.NOT_FOUND)

    # Verify that the competition event belongs to the active competition.
    comp = comp_event.Competition
    if not comp.active:
        return (ERR_MSG_INACTIVE_COMP, HTTPStatus.BAD_REQUEST)

    # Retrieve the user's results record for this event if they exist, or else create a new record
    user_event_results = get_event_results_for_user(comp_event_id, current_user)
    if not user_event_results:
        user_event_results = UserEventResults(comp_event_id=comp_event_id,
                                              user_id=current_user.id)

    # Create the record for this solve and associate it with the user's event results
    solve = UserSolve(time=centiseconds, is_dnf=is_dnf, is_plus_two=is_plus_two,
                      scramble_id=scramble_id)
    user_event_results.solves.append(solve)

    # Process through the user's event results, ensuring PB flags, best single, average, overall
    # event result, etc are all up-to-date.
    process_event_results(user_event_results, comp_event, current_user)
    save_event_results(user_event_results)

    # We don't need to return any info, just indicate intentionally empty.
    return ('', HTTPStatus.NO_CONTENT)
