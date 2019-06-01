""" Routes related to saving results to the database. """

import json

from http import HTTPStatus

from flask import request, abort
from flask_login import current_user

from app import app
from app.business.user_results.creation import process_event_results
from app.persistence.models import UserSolve, UserEventResults
from app.persistence.comp_manager import get_comp_event_by_id
from app.persistence.user_results_manager import save_event_results, get_event_results_for_user,\
    delete_user_solve, delete_event_results

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

COMMENT = 'comment'

ERR_MSG_MISSING_INFO = 'Some required information is missing from your solve.'
ERR_MSG_NO_SUCH_EVENT = "Can't find a competition event with ID {}."
ERR_MSG_INACTIVE_COMP = 'This event belongs to a competition which has ended.'
ERR_MSG_NO_RESULTS    = "Can't find user results for competition event with ID {}."

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
        user_event_results = UserEventResults(comp_event_id=comp_event_id, user_id=current_user.id,
                                              comment='')

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


@app.route('/toggle_prev_dnf', methods=['POST'])
def toggle_prev_dnf():
    """ Toggles the DNF status of the last solve for the specified user and competition event. """

    if not current_user.is_authenticated:
        return abort(HTTPStatus.UNAUTHORIZED)

    # Extract JSON solve data, deserialize to dict, and verify that all expected fields are present
    solve_data = json.loads(request.data)
    if not all(key in solve_data for key in (COMP_EVENT_ID,)):
        return (ERR_MSG_MISSING_INFO, HTTPStatus.BAD_REQUEST)

    # Extract all the specific fields out of the solve data dictionary
    comp_event_id = solve_data[COMP_EVENT_ID]

    # Retrieve the specified competition event
    comp_event = get_comp_event_by_id(comp_event_id)
    if not comp_event:
        return (ERR_MSG_NO_SUCH_EVENT.format(comp_event_id), HTTPStatus.NOT_FOUND)

    # Verify that the competition event belongs to the active competition.
    comp = comp_event.Competition
    if not comp.active:
        return (ERR_MSG_INACTIVE_COMP, HTTPStatus.BAD_REQUEST)

    # Retrieve the user's results record for this event
    user_event_results = get_event_results_for_user(comp_event_id, current_user)
    if (not user_event_results) or (not user_event_results.solves):
        return (ERR_MSG_NO_RESULTS.format(comp_event_id), HTTPStatus.NOT_FOUND)

    # Grab the last completed solve, and toggle DNF for it
    previous_solve = user_event_results.solves[-1]
    previous_solve.is_dnf = not previous_solve.is_dnf

    # If the solve now has DNF, ensure it doesn't also have +2
    if previous_solve.is_dnf:
        previous_solve.is_plus_two = False

    # Process through the user's event results, ensuring PB flags, best single, average, overall
    # event result, etc are all up-to-date.
    process_event_results(user_event_results, comp_event, current_user)
    save_event_results(user_event_results)

    # We don't need to return any info, just indicate intentionally empty.
    return ('', HTTPStatus.NO_CONTENT)


@app.route('/toggle_prev_plus_two', methods=['POST'])
def toggle_prev_plus_two():
    """ Toggles the +2 status of the last solve for the specified user and competition event. """

    if not current_user.is_authenticated:
        return abort(HTTPStatus.UNAUTHORIZED)

    # Extract JSON solve data, deserialize to dict, and verify that all expected fields are present
    solve_data = json.loads(request.data)
    if not all(key in solve_data for key in (COMP_EVENT_ID,)):
        return (ERR_MSG_MISSING_INFO, HTTPStatus.BAD_REQUEST)

    # Extract all the specific fields out of the solve data dictionary
    comp_event_id = solve_data[COMP_EVENT_ID]

    # Retrieve the specified competition event
    comp_event = get_comp_event_by_id(comp_event_id)
    if not comp_event:
        return (ERR_MSG_NO_SUCH_EVENT.format(comp_event_id), HTTPStatus.NOT_FOUND)

    # Verify that the competition event belongs to the active competition.
    comp = comp_event.Competition
    if not comp.active:
        return (ERR_MSG_INACTIVE_COMP, HTTPStatus.BAD_REQUEST)

    # Retrieve the user's results record for this event
    user_event_results = get_event_results_for_user(comp_event_id, current_user)
    if (not user_event_results) or (not user_event_results.solves):
        return (ERR_MSG_NO_RESULTS.format(comp_event_id), HTTPStatus.NOT_FOUND)

    # Grab the last completed solve, and toggle +2 for it
    previous_solve = user_event_results.solves[-1]
    previous_solve.is_plus_two = not previous_solve.is_plus_two

    # If the solve now has +2, ensure it doesn't also have DNF
    if previous_solve.is_plus_two:
        previous_solve.is_dnf = False

    # Process through the user's event results, ensuring PB flags, best single, average, overall
    # event result, etc are all up-to-date.
    process_event_results(user_event_results, comp_event, current_user)
    save_event_results(user_event_results)

    # We don't need to return any info, just indicate intentionally empty.
    return ('', HTTPStatus.NO_CONTENT)


@app.route('/delete_prev_solve', methods=['POST'])
def delete_prev_solve():
    """ Deletes the last completed solve of the specified competition event for this user. """

    if not current_user.is_authenticated:
        return abort(HTTPStatus.UNAUTHORIZED)

    # Extract JSON solve data, deserialize to dict, and verify that all expected fields are present
    solve_data = json.loads(request.data)
    if not all(key in solve_data for key in (COMP_EVENT_ID,)):
        return (ERR_MSG_MISSING_INFO, HTTPStatus.BAD_REQUEST)

    # Extract all the specific fields out of the solve data dictionary
    comp_event_id = solve_data[COMP_EVENT_ID]

    # Retrieve the specified competition event
    comp_event = get_comp_event_by_id(comp_event_id)
    if not comp_event:
        return (ERR_MSG_NO_SUCH_EVENT.format(comp_event_id), HTTPStatus.NOT_FOUND)

    # Verify that the competition event belongs to the active competition.
    comp = comp_event.Competition
    if not comp.active:
        return (ERR_MSG_INACTIVE_COMP, HTTPStatus.BAD_REQUEST)

    # Retrieve the user's results record for this event
    user_event_results = get_event_results_for_user(comp_event_id, current_user)
    if (not user_event_results) or (not user_event_results.solves):
        return (ERR_MSG_NO_RESULTS.format(comp_event_id), HTTPStatus.NOT_FOUND)

    # If the results only have one solve (which we're about to delete), we need to delete the
    # results entirely
    do_delete_user_results_after_solve = len(user_event_results.solves) == 1

    # Grab the last completed solve and delete it
    previous_solve = user_event_results.solves[-1]
    delete_user_solve(previous_solve)

    # If no more solves left, just delete the whole results record
    if do_delete_user_results_after_solve:
        delete_event_results(user_event_results)

    # Otherwise process through the user's event results, ensuring PB flags, best single, average,
    # overall event result, etc are all up-to-date.
    else:
        process_event_results(user_event_results, comp_event, current_user)
        save_event_results(user_event_results)

    # We don't need to return any info, just indicate intentionally empty.
    return ('', HTTPStatus.NO_CONTENT)


@app.route('/apply_comment', methods=['POST'])
def apply_comment():
    """ Applies the supplied comment to the desired competition event for this user. """

    if not current_user.is_authenticated:
        return abort(HTTPStatus.UNAUTHORIZED)

    # Extract JSON solve data, deserialize to dict, and verify that all expected fields are present
    solve_data = json.loads(request.data)
    if not all(key in solve_data for key in (COMP_EVENT_ID, COMMENT)):
        return (ERR_MSG_MISSING_INFO, HTTPStatus.BAD_REQUEST)

    # Extract all the specific fields out of the solve data dictionary
    comp_event_id = solve_data[COMP_EVENT_ID]
    comment       = solve_data[COMMENT]

    # Retrieve the specified competition event
    comp_event = get_comp_event_by_id(comp_event_id)
    if not comp_event:
        return (ERR_MSG_NO_SUCH_EVENT.format(comp_event_id), HTTPStatus.NOT_FOUND)

    # Verify that the competition event belongs to the active competition.
    comp = comp_event.Competition
    if not comp.active:
        return (ERR_MSG_INACTIVE_COMP, HTTPStatus.BAD_REQUEST)

    # Retrieve the user's results record for this event
    user_event_results = get_event_results_for_user(comp_event_id, current_user)
    if (not user_event_results) or (not user_event_results.solves):
        return (ERR_MSG_NO_RESULTS.format(comp_event_id), HTTPStatus.NOT_FOUND)

    # Apply the new comment and save the results
    user_event_results.comment = comment
    save_event_results(user_event_results)

    # We don't need to return any info, just indicate intentionally empty.
    return ('', HTTPStatus.NO_CONTENT)
