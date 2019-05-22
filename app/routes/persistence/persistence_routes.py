""" Routes related to saving results to the database. """

import traceback
import json

from flask import request, abort
from flask_login import current_user

from app import app
from app.business.user_results.creation import build_user_event_results
from app.persistence.user_manager import get_user_by_username
from app.persistence.user_results_manager import save_event_results_for_user
from app.persistence.models import UserEventResults

# -------------------------------------------------------------------------------------------------

LOG_EVENT_RESULTS_TEMPLATE = "{}: submitted {} results"
LOG_RESULTS_ERROR_TEMPLATE = "{}: error creating or saving {} results"
LOG_SAVED_RESULTS_TEMPLATE = "{}: saved {} results"

# -------------------------------------------------------------------------------------------------

@app.route('/save_event', methods=['POST'])
def save_event():
    """ A route for saving a specific event to the database. """

    if not current_user.is_authenticated:
        app.logger.warning('unauthenticated user attempting save_event')
        return abort(400)

    try:
        user = get_user_by_username(current_user.username)
        event_result, event_name = build_user_event_results(request.get_json(), user)

        app.logger.info(LOG_EVENT_RESULTS_TEMPLATE.format(user.username, event_name),
                        extra=__create_results_log_context(user, event_name, event_result))

        saved_results = save_event_results_for_user(event_result, user)
        app.logger.info(LOG_SAVED_RESULTS_TEMPLATE.format(user.username, event_name))

        # Build up a dictionary of relevant information about the event results so far, to include
        # the summary (aka times string), PB flags, single and average, and complete status
        event_info = {
            'single':       saved_results.friendly_single(),
            'wasPbSingle':  saved_results.was_pb_single,
            'average':      saved_results.friendly_average(),
            'wasPbAverage': saved_results.was_pb_average,
            'summary':      saved_results.times_string,
            'result':       saved_results.friendly_result(),
        }
        return json.dumps(event_info)

    # TODO: Figure out specific exceptions that can happen here, probably mostly Reddit ones
    except Exception as ex:
        app.logger.info(LOG_RESULTS_ERROR_TEMPLATE.format(user.username, "whatever"),
                        extra=__create_results_error_log_context(user, ex))
        return abort(500, str(ex))

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
