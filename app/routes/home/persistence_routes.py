""" Routes related to saving results to the database. """

import traceback
import json

from flask import request, abort, url_for
from flask_login import current_user

from app import app
from app.business.user_results.creation import build_user_event_results, build_event_summary
from app.business.user_results.blacklisting import take_blacklist_action_if_necessary
from app.persistence.user_manager import get_user_by_username
from app.persistence.user_results_manager import save_event_results_for_user,\
    are_results_different_than_existing, get_comment_id_by_comp_id_and_user,\
    get_event_results_for_user
from app.persistence.models import UserEventResults
from app.util.reddit import get_permalink_for_user_and_comment
from app.tasks.reddit import submit_reddit_comment

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

        # Check if these event results should be autoblacklisted, and set their blacklist flag
        # notes if so.
        # NOTE: don't do this check directly inside `build_user_event_results` above, because
        # other code paths use that. We only need to do the autoblacklist check before actually
        # saving results
        event_result = take_blacklist_action_if_necessary(event_result)

        app.logger.info(LOG_EVENT_RESULTS_TEMPLATE.format(user.username, event_name),
                        extra=__create_results_log_context(user, event_name, event_result))

        # Figure out if we need to repost the results to Reddit or not
        if event_result.is_complete:
            # If these results are complete, but different than what's already there, we should
            # submit again because it means the user altered a time (add/remove penalty,
            # manual time entry, etc)
            should_do_reddit_submit = are_results_different_than_existing(event_result, user)
        else:
            # If these results are incomplete, and the user currently has complete results saved,
            # it means they deleted a time. The event will no longer be complete, and so we should
            # submit again to delete that event
            previous_results = get_event_results_for_user(event_result.comp_event_id, user)
            should_do_reddit_submit = previous_results and previous_results.is_complete

        saved_results = save_event_results_for_user(event_result, user)
        app.logger.info(LOG_SAVED_RESULTS_TEMPLATE.format(user.username, event_name))

        if should_do_reddit_submit:
            # Need to build the profile url here so the app context is available.
            # Can't do it inside the task, which runs separately without the app context
            profile_url = url_for('profile', username=user.username)
            app.logger.info("{}: queuing submission to reddit".format(user.username))
            submit_reddit_comment(saved_results.CompetitionEvent.Competition.id, user.id, profile_url)

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


@app.route('/event_summaries', methods=['POST'])
def get_event_summaries():
    """ A route for building an event summary which details the average or best (depending on
    the event format), and the constituent times with penalties, and best/worst indicated when
    appropriate.

    Ex: 15.24 = 14.09, 16.69, 14.94, (10.82), (18.39) --> for a Ao5 event
        6:26.83 = 6:46.17, 5:50.88, 6:43.44           --> for a Mo3 event """

    data = request.get_json()
    summaries = {event['comp_event_id']: build_event_summary(event, None) for event in data}

    return json.dumps(summaries)


@app.route('/comment_url/<int:comp_id>')
def comment_url(comp_id):
    """ A route for retrieving the user's Reddit comment direct URL for a given comp event. """

    if not current_user.is_authenticated:
        return ""

    user = get_user_by_username(current_user.username)
    comment_id = get_comment_id_by_comp_id_and_user(comp_id, user.id)
    if not comment_id:
        return ""

    return get_permalink_for_user_and_comment(user, comment_id)

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
