""" Routes related to submitting results to Reddit. """

import json

from flask import render_template, request
from flask_login import current_user

from app import CUBERS_APP
from app.persistence import comp_manager
from app.persistence.user_manager import get_user_by_username
from app.persistence.user_results_manager import build_all_user_results,\
     save_event_results_for_user, determine_if_resubmit
from app.util.reddit_util import build_comment_source_from_events_results,\
     submit_comment_for_user, get_permalink_for_comp_thread, update_comment_for_user

# -------------------------------------------------------------------------------------------------

COMMENT_SUCCESS_TEMPLATE = 'submit/comment_submit_success.html'
COMMENT_FAILURE_TEMPLATE = 'submit/comment_submit_failure.html'
COMMENT_SOURCE_TEMPLATE  = 'submit/times_comment_source.html'
SAVE_SUCCESS_BUT_NO_COMMENT_TEMPLATE = 'submit/saved_but_no_comment.html'

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route('/submit', methods=['POST'])
def submit_times():
    """ A route for submitting user times for a competition. If the user is authenticated, save
    the times to the database as an intermediate step. Generate source for a /r/cubers comp
    thread comment. If the user is authenticated, submit the comment for them, or else
    redirect to a page where the comment source is displayed. """

    #TODO Clean this garbage up, my god

    #TODO Figure out how to handle it if authenticated user is only submitting incomplete events
    # nothing to submit to reddit, but still need to save to database

    data = request.form['input-results']

    user_events    = json.loads(data)
    user_results   = build_all_user_results(user_events)
    comment_source = build_comment_source_from_events_results(user_results)

    comp = comp_manager.get_active_competition()
    reddit_thread_id = comp.reddit_thread_id
    comp_thread_url = get_permalink_for_comp_thread(reddit_thread_id)

    if current_user.is_authenticated:
        user = get_user_by_username(current_user.username)
        try:
            url, comment_id = do_reddit_submit(user, user_results, comment_source, reddit_thread_id)
            for result in user_results:
                if comment_id:
                    result.reddit_comment = comment_id
                save_event_results_for_user(result, user)

            if comment_id:
                return render_template(COMMENT_SUCCESS_TEMPLATE, comment_url=url,
                                    current_competition=comp)

            return render_template(SAVE_SUCCESS_BUT_NO_COMMENT_TEMPLATE, current_competition=comp)
            
        except Exception as ex:
            # TODO figure out what exceptions can be thrown here
            import sys
            import traceback
            print(ex, file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return render_template(COMMENT_FAILURE_TEMPLATE, comment_source=comment_source,
                                   comp_url=comp_thread_url, current_competition=comp)

    # show comment source page
    return render_template(COMMENT_SOURCE_TEMPLATE, comment_source=comment_source,
                           comp_url=comp_thread_url, current_competition=comp)

# -------------------------------------------------------------------------------------------------

def do_reddit_submit(user, user_results, comment_source, comp_reddit_thread_id):
    """ Handle submitting a new, or updating an existing, Reddit comment. Returns a tuple of
    the Reddit comment URL and the comment ID. """

    anything_to_post = any(_.is_complete() for _ in user_results)
    if not anything_to_post:
        return None, None

    previous_comment_id = determine_if_resubmit(user_results, user)

    # this is a resubmission
    if previous_comment_id:
        return update_comment_for_user(user, previous_comment_id, comment_source)

    # new submission
    return submit_comment_for_user(user, comp_reddit_thread_id, comment_source)