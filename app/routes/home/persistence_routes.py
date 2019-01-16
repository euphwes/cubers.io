""" Routes related to saving results to the database. """

import json

from flask import request, abort
from flask_login import current_user

from app import CUBERS_APP
from app.business.user_results import build_user_event_results, build_event_summary,\
    determine_if_should_be_autoblacklisted
from app.persistence.user_manager import get_user_by_username
from app.persistence.user_results_manager import save_event_results_for_user,\
    are_results_different_than_existing, get_comment_id_by_comp_id_and_user,\
    get_event_results_for_user, get_all_complete_user_results_for_comp_and_user
from app.persistence.comp_manager import get_competition
from app.util.reddit_util import build_comment_source_from_events_results, submit_comment_for_user,\
    update_comment_for_user, get_permalink_for_user_and_comment

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route('/save_event', methods=['POST'])
def save_event():
    """ A route for saving a specific event to the database. """

    if not current_user.is_authenticated:
        return abort(400, "authenticated users only")

    try:
        user = get_user_by_username(current_user.username)
        event_result = build_user_event_results(request.get_json(), user)

        # Check if these event results should be autoblacklisted, and set their blacklist flag
        # notes if so.
        # NOTE: don't do this check directly inside `build_user_event_results` above, because
        # other code paths use that. We only need to do the autoblacklist check before actually
        # saving results
        event_result = determine_if_should_be_autoblacklisted(event_result)

        # Figure out if we need to repost the results to Reddit or not
        if event_result.is_complete:
            # Ff these results are complete, but different than what's already there, we should
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

        if should_do_reddit_submit:
            do_reddit_submit(saved_results.CompetitionEvent.Competition.id, user)

        # Build up a dictionary of relevant information about the event results so far, to include
        # the summary (aka times string), PB flags, single and average, and complete status
        event_info = {
            'isComplete'  : saved_results.is_complete,
            'single'      : saved_results.friendly_single(),
            'wasPbSingle' : saved_results.was_pb_single,
            'average'     : saved_results.friendly_average(),
            'wasPbAverage': saved_results.was_pb_average,
            'summary'     : saved_results.times_string,
            'result'      : saved_results.friendly_result(),
        }
        return json.dumps(event_info)

    # TODO: Figure out specific exceptions that can happen here, probably mostly Reddit ones
    # pylint: disable=W0703
    except Exception as ex:
        return abort(500, str(ex))


@CUBERS_APP.route('/event_summaries', methods=['POST'])
def get_event_summaries():
    """ A route for building an event summary which details the average or best (depending on
    the event format), and the constituent times with penalties, and best/worst indicated when
    appropriate.

    Ex: 15.24 = 14.09, 16.69, 14.94, (10.82), (18.39) --> for a Ao5 event
        6:26.83 = 6:46.17, 5:50.88, 6:43.44           --> for a Mo3 event """

    data = request.get_json()
    summaries = {event['comp_event_id']: build_event_summary(event, None) for event in data}

    return json.dumps(summaries)


@CUBERS_APP.route('/comment_url/<int:comp_id>')
def comment_url(comp_id):
    """ A route for retrieving the user's Reddit comment direct URL for a given comp event. """

    if not current_user.is_authenticated:
        return ""

    user = get_user_by_username(current_user.username)
    comment_id = get_comment_id_by_comp_id_and_user(comp_id, user)
    if not comment_id:
        return ""

    return get_permalink_for_user_and_comment(user, comment_id)


def do_reddit_submit(comp_id, user):
    """ Handle submitting a new, or updating an existing, Reddit comment. """

    # TODO: probably should put this in the Reddit util

    comp = get_competition(comp_id)
    reddit_thread_id = comp.reddit_thread_id
    results = get_all_complete_user_results_for_comp_and_user(comp.id, user.id)
    comment_source = build_comment_source_from_events_results(results, user.username)

    previous_comment_id = get_comment_id_by_comp_id_and_user(comp.id, user)

    # this is a resubmission
    if previous_comment_id:
        _, comment_id = update_comment_for_user(user, previous_comment_id, comment_source)

    # new submission
    else:
        _, comment_id = submit_comment_for_user(user, reddit_thread_id, comment_source)

    if not comment_id:
        return

    for result in results:
        result.reddit_comment = comment_id
        save_event_results_for_user(result, user)
