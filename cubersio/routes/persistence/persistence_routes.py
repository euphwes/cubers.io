""" Routes related to saving results to the database. """

import json

from http import HTTPStatus

from flask import request
from flask_login import current_user

from cubersio import app
from cubersio.business.user_results.creation import process_event_results
from cubersio.persistence.models import UserSolve, UserEventResults
from cubersio.persistence.comp_manager import get_comp_event_by_id
from cubersio.persistence.user_results_manager import save_event_results, get_event_results_for_user,\
    delete_user_solve, delete_event_results, get_user_solve_for_scramble_id
from cubersio.util.events.mbld import MbldSolve
from cubersio.routes.timer import timer_page
from cubersio.routes import api_login_required

# -------------------------------------------------------------------------------------------------

LOG_EVENT_RESULTS_TEMPLATE = "{}: submitted {} results"
LOG_RESULTS_ERROR_TEMPLATE = "{}: error creating or saving {} results"
LOG_SAVED_RESULTS_TEMPLATE = "{}: saved {} results"

# Solve data dictionary keys
IS_DNF            = 'is_dnf'
IS_PLUS_TWO       = 'is_plus_two'
SCRAMBLE_ID       = 'scramble_id'
COMP_EVENT_ID     = 'comp_event_id'
CENTISECONDS      = 'elapsed_centiseconds'
IS_INSPECTION_DNF = 'is_inspection_dnf'
SOLVE_ID          = 'solve_id'
PENALTY_TO_TOGGLE = 'penalty_to_toggle'
PENALTY_DNF       = 'penalty_dnf'
PENALTY_PLUS_TWO  = 'penalty_plus_two'
FMC_COMMENT       = 'fmc_comment'
EXPECTED_FIELDS   = (IS_DNF, IS_PLUS_TWO, SCRAMBLE_ID, COMP_EVENT_ID, CENTISECONDS)

COMMENT = 'comment'

ERR_MSG_MISSING_INFO           = 'Some required information is missing from your solve.'
ERR_MSG_NO_SUCH_EVENT          = "Can't find a competition event with ID {}."
ERR_MSG_INACTIVE_COMP          = 'This event belongs to a competition which has ended.'
ERR_MSG_NO_RESULTS             = "Can't find user results for competition event with ID {}."
ERR_MSG_NO_SOLVE               = "Can't find solve with ID {} that belongs to {}."
ERR_MSG_NOT_VALID_FOR_FMC      = 'This operation is not valid for FMC!'
ERR_MSG_NON_POSITIVE_TIME      = 'Solve time cannot be zero or negative!'
ERR_MSG_MBLD_TOO_FEW_ATTEMPTED = "You must attempt at least 2 cubes for MBLD!"

# -------------------------------------------------------------------------------------------------
# Below are routes called during standard usage of the timer pages
# -------------------------------------------------------------------------------------------------

@app.route('/post_solve', methods=['POST'])
@api_login_required
def post_solve():
    """ Saves a solve. Ensures the user has UserEventResults for this event, associated this solve
    with those results, and processes the results to make sure all relevant data is up-to-date. """

    # Extract JSON solve data, deserialize to dict, and verify that all expected fields are present
    solve_data = json.loads(request.data)
    if not all(key in solve_data for key in EXPECTED_FIELDS):
        return (ERR_MSG_MISSING_INFO, HTTPStatus.BAD_REQUEST)

    # Extract all the specific fields out of the solve data dictionary
    is_dnf            = solve_data[IS_DNF]
    is_plus_two       = solve_data[IS_PLUS_TWO]
    scramble_id       = solve_data[SCRAMBLE_ID]
    comp_event_id     = solve_data[COMP_EVENT_ID]
    centiseconds      = solve_data[CENTISECONDS]
    is_inspection_dnf = solve_data.get(IS_INSPECTION_DNF, False)
    fmc_comment       = solve_data.get(FMC_COMMENT, '')

    # If the solve time isn't positive, don't save the solve. Let the user know that a negative
    # time isn't allowed.
    if centiseconds <= 0:
        return (ERR_MSG_NON_POSITIVE_TIME, HTTPStatus.BAD_REQUEST)

    # If the submitted solve is for a scramble the user already has a solve for,
    # don't take any further action to persist a solve, just return. User probably
    # is user manual time entry and pressed enter twice accidentally in quick succession
    if get_user_solve_for_scramble_id(current_user.id, scramble_id):
        return timer_page(comp_event_id, gather_info_for_live_refresh=True)

    # Retrieve the specified competition event
    comp_event = get_comp_event_by_id(comp_event_id)
    if not comp_event:
        return (ERR_MSG_NO_SUCH_EVENT.format(comp_event_id), HTTPStatus.NOT_FOUND)

    # Verify that the competition event belongs to the active competition.
    comp = comp_event.Competition
    if not comp.active:
        return (ERR_MSG_INACTIVE_COMP, HTTPStatus.BAD_REQUEST)

    # Double-check that if the solve is MBLD, the number of attempted cubes is > 1
    if comp_event.Event.name == "MBLD":
        if MbldSolve(centiseconds).attempted < 2:
            return (ERR_MSG_MBLD_TOO_FEW_ATTEMPTED, HTTPStatus.BAD_REQUEST)

    # Retrieve the user's results record for this event if they exist, or else create a new record
    user_event_results = get_event_results_for_user(comp_event_id, current_user)
    if not user_event_results:
        user_event_results = UserEventResults(comp_event_id=comp_event_id, user_id=current_user.id,
                                              comment='')

    # Create the record for this solve and associate it with the user's event results
    solve = UserSolve(time=centiseconds, is_dnf=is_dnf, is_plus_two=is_plus_two,
                      scramble_id=scramble_id, is_inspection_dnf=is_inspection_dnf,
                      fmc_explanation=fmc_comment)
    user_event_results.solves.append(solve)

    # Process through the user's event results, ensuring PB flags, best single, average, overall
    # event result, etc are all up-to-date.
    process_event_results(user_event_results, comp_event, current_user)
    save_event_results(user_event_results)

    return timer_page(comp_event_id, gather_info_for_live_refresh=True)


@app.route('/toggle_prev_penalty', methods=['POST'])
@api_login_required
def toggle_prev_penalty():
    """ Toggles the either the DNF or +2 status of the last solve for the specified user and
    competition event. """

    # Extract JSON solve data, deserialize to dict, and verify that all expected fields are present
    solve_data = json.loads(request.data)
    if not all(key in solve_data for key in (COMP_EVENT_ID,)):
        return (ERR_MSG_MISSING_INFO, HTTPStatus.BAD_REQUEST)

    # Extract all the specific fields out of the solve data dictionary
    comp_event_id = solve_data[COMP_EVENT_ID]
    penalty_to_toggle = solve_data[PENALTY_TO_TOGGLE]

    # Retrieve the specified competition event
    comp_event = get_comp_event_by_id(comp_event_id)
    if not comp_event:
        return (ERR_MSG_NO_SUCH_EVENT.format(comp_event_id), HTTPStatus.NOT_FOUND)

    # If this is FMC, this isn't valid
    if comp_event.Event.name == 'FMC':
        return (ERR_MSG_NOT_VALID_FOR_FMC, HTTPStatus.BAD_REQUEST)

    # Verify that the competition event belongs to the active competition.
    comp = comp_event.Competition
    if not comp.active:
        return (ERR_MSG_INACTIVE_COMP, HTTPStatus.BAD_REQUEST)

    # Retrieve the user's results record for this event
    user_event_results = get_event_results_for_user(comp_event_id, current_user)
    if (not user_event_results) or (not user_event_results.solves):
        return (ERR_MSG_NO_RESULTS.format(comp_event_id), HTTPStatus.NOT_FOUND)

    # Grab the last completed solve
    previous_solve = user_event_results.solves[-1]

    if penalty_to_toggle == PENALTY_DNF:
        # Toggle DNF
        # If the solve now has DNF, ensure it doesn't also have +2
        previous_solve.is_dnf = not previous_solve.is_dnf
        if previous_solve.is_dnf:
            previous_solve.is_plus_two = False

    else:
        # Toggle +2
        # If the solve now has +2, ensure it doesn't also have DNF
        previous_solve.is_plus_two = not previous_solve.is_plus_two
        if previous_solve.is_plus_two:
            previous_solve.is_dnf = False

    # Process through the user's event results, ensuring PB flags, best single, average, overall
    # event result, etc are all up-to-date.
    process_event_results(user_event_results, comp_event, current_user)
    save_event_results(user_event_results)

    return timer_page(comp_event_id, gather_info_for_live_refresh=True)


@app.route('/delete_prev_solve', methods=['POST'])
@api_login_required
def delete_prev_solve():
    """ Deletes the last completed solve of the specified competition event for this user. """

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

    return timer_page(comp_event_id, gather_info_for_live_refresh=True)


@app.route('/apply_comment', methods=['POST'])
@api_login_required
def apply_comment():
    """ Applies the supplied comment to the desired competition event for this user. """

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

    return timer_page(comp_event_id, gather_info_for_live_refresh=True)

# -------------------------------------------------------------------------------------------------
# Below are routes called by the timer page solve context menu
# -------------------------------------------------------------------------------------------------

@app.route('/set_time', methods=['POST'])
@api_login_required
def set_time():
    """ Applies the specified time to the specified solve. """

    target_solve_data, err_msg, http_status_code = __retrieve_target_solve(request.data, current_user)
    if not target_solve_data:
        return err_msg, http_status_code

    # Extract the target solve, user's event results, and the associated competition event
    target_solve, user_event_results, comp_event = target_solve_data

    # If this is FMC, this isn't valid
    if comp_event.Event.name == 'FMC':
        return (ERR_MSG_NOT_VALID_FOR_FMC, HTTPStatus.BAD_REQUEST)

    # Extract JSON solve data, deserialize to dict, and verify that all expected fields are present
    # This is slightly redundant given the call to __retrieve_target_solve, but we also need to pull
    # the centiseconds value which that doesn't do.
    solve_data = json.loads(request.data)
    if not all(key in solve_data for key in (SOLVE_ID, COMP_EVENT_ID, CENTISECONDS)):
        return (ERR_MSG_MISSING_INFO, HTTPStatus.BAD_REQUEST)

    # Extract all the specific fields out of the solve data dictionary
    target_solve.time = solve_data[CENTISECONDS]

    # If the solve time isn't positive, don't save the solve. Let the user know that a negative
    # time isn't allowed.
    if target_solve.time <= 0:
        return (ERR_MSG_NON_POSITIVE_TIME, HTTPStatus.BAD_REQUEST)

    # No penalties on the solve after adjusting time
    target_solve.is_plus_two = False
    target_solve.is_dnf = False

    process_event_results(user_event_results, comp_event, current_user)
    save_event_results(user_event_results)

    return timer_page(comp_event.id, gather_info_for_live_refresh=True)


@app.route('/set_plus_two', methods=['POST'])
@api_login_required
def set_plus_two():
    """ Applies +2 to the specified solve. """

    target_solve_data, err_msg, http_status_code = __retrieve_target_solve(request.data, current_user)
    if not target_solve_data:
        return err_msg, http_status_code

    # Extract the target solve, user's event results, and the associated competition event
    target_solve, user_event_results, comp_event = target_solve_data

    # If this is FMC, this isn't valid
    if comp_event.Event.name == 'FMC':
        return (ERR_MSG_NOT_VALID_FOR_FMC, HTTPStatus.BAD_REQUEST)

    # Make the target solve +2, and ensure it's not DNF
    target_solve.is_plus_two = True
    target_solve.is_dnf = False

    process_event_results(user_event_results, comp_event, current_user)
    save_event_results(user_event_results)

    return timer_page(comp_event.id, gather_info_for_live_refresh=True)


@app.route('/set_dnf', methods=['POST'])
@api_login_required
def set_dnf():
    """ Applies DNF to the specified solve. """

    target_solve_data, err_msg, http_status_code = __retrieve_target_solve(request.data, current_user)
    if not target_solve_data:
        return err_msg, http_status_code

    # Extract the target solve, user's event results, and the associated competition event
    target_solve, user_event_results, comp_event = target_solve_data

    # If this is FMC, this isn't valid
    if comp_event.Event.name == 'FMC':
        return (ERR_MSG_NOT_VALID_FOR_FMC, HTTPStatus.BAD_REQUEST)

    # Make the target solve DNF, and ensure it's not +2
    target_solve.is_dnf = True
    target_solve.is_plus_two = False

    process_event_results(user_event_results, comp_event, current_user)
    save_event_results(user_event_results)

    return timer_page(comp_event.id, gather_info_for_live_refresh=True)


@app.route('/clear_penalty', methods=['POST'])
@api_login_required
def clear_penalty():
    """ Clears penalties from the specified solve. """

    target_solve_data, err_msg, http_status_code = __retrieve_target_solve(request.data, current_user)
    if not target_solve_data:
        return err_msg, http_status_code

    # Extract the target solve, user's event results, and the associated competition event
    target_solve, user_event_results, comp_event = target_solve_data

    # If this is FMC, this isn't valid
    if comp_event.Event.name == 'FMC':
        return (ERR_MSG_NOT_VALID_FOR_FMC, HTTPStatus.BAD_REQUEST)

    # Clear penalties
    target_solve.is_plus_two = False
    target_solve.is_dnf = False

    process_event_results(user_event_results, comp_event, current_user)
    save_event_results(user_event_results)

    return timer_page(comp_event.id, gather_info_for_live_refresh=True)


@app.route('/delete_solve', methods=['POST'])
@api_login_required
def delete_solve():
    """ Deletes the specified solve. """

    target_solve_data, err_msg, http_status_code = __retrieve_target_solve(request.data, current_user)
    if not target_solve_data:
        return err_msg, http_status_code

    # Extract the target solve, user's event results, and the associated comp event
    target_solve, user_event_results, comp_event = target_solve_data

    # If the results only have one solve (which we're about to delete),
    # we need to delete the results entirely
    do_delete_user_results_after_solve = len(user_event_results.solves) == 1

    # Delete the target solve
    delete_user_solve(target_solve)

    # If no more solves left, just delete the whole results record
    if do_delete_user_results_after_solve:
        delete_event_results(user_event_results)

    # Otherwise process through the user's event results, ensuring PB flags, best single, average,
    # overall event result, etc are all up-to-date.
    else:
        process_event_results(user_event_results, comp_event, current_user)
        save_event_results(user_event_results)

    return timer_page(comp_event.id, gather_info_for_live_refresh=True)

# -------------------------------------------------------------------------------------------------

def __retrieve_target_solve(request_data, user):
    """ Utility method to retrieve the specified solve (by solve id and competition event id).
    Validates the solve belongs to an active competition, and belongs to the specified user.
    Returns the following shapes:
        ((target_solve, user_event_results, comp_event), None, None)
            if the solve exists, in the active comp, for the specified user.
        (None, err_msg, http_status_code)
            if something goes wrong during retrieval. """

    # Extract JSON solve data, deserialize to dict, and verify that all expected fields are present
    solve_data = json.loads(request_data)
    if not all(key in solve_data for key in (SOLVE_ID, COMP_EVENT_ID)):
        return None, ERR_MSG_MISSING_INFO, HTTPStatus.BAD_REQUEST

    # Extract all the specific fields out of the solve data dictionary
    solve_id = solve_data[SOLVE_ID]
    comp_event_id = solve_data[COMP_EVENT_ID]

    # Retrieve the specified competition event
    comp_event = get_comp_event_by_id(comp_event_id)
    if not comp_event:
        return None, ERR_MSG_NO_SUCH_EVENT.format(comp_event_id), HTTPStatus.NOT_FOUND

    # Verify that the competition event belongs to the active competition.
    comp = comp_event.Competition
    if not comp.active:
        return ERR_MSG_INACTIVE_COMP, HTTPStatus.BAD_REQUEST

    # Retrieve the user's results record for this event
    user_event_results = get_event_results_for_user(comp_event_id, user)
    if (not user_event_results) or (not user_event_results.solves):
        return None, ERR_MSG_NO_RESULTS.format(comp_event_id), HTTPStatus.NOT_FOUND

    # Find the target solve in the user's results
    target_solve = None
    for solve in user_event_results.solves:
        if solve.id == solve_id:
            target_solve = solve
            break

    # If we didn't find the target solve, let the user know
    if not target_solve:
        return None, ERR_MSG_NO_SOLVE.format(solve_id, user.username), HTTPStatus.NOT_FOUND

    return (target_solve, user_event_results, comp_event), None, None
