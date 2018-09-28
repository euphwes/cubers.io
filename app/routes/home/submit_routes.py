""" Routes related to submitting results to Reddit. """

import json

from flask import render_template, request
from flask_login import current_user

from app import CUBERS_APP
from app.persistence import comp_manager
from app.persistence.user_manager import get_user_by_username
from app.persistence.user_results_manager import build_all_user_results,\
     save_event_results_for_user, get_event_results_for_user
from app.util.reddit_util import build_comment_source_from_events_results,\
     submit_comment_for_user, get_permalink_for_comp_thread, update_comment_for_user

# -------------------------------------------------------------------------------------------------

COMMENT_SUCCESS_TEMPLATE = 'submit/comment_submit_success.html'
COMMENT_FAILURE_TEMPLATE = 'submit/comment_submit_failure.html'
COMMENT_SOURCE_TEMPLATE  = 'submit/times_comment_source.html'

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
    comp_reddit_id = comp.reddit_thread_id
    comp_thread_url = get_permalink_for_comp_thread(comp_reddit_id)

    for results in user_results:
        if results.is_complete():
            any_complete_to_post = True
            break

    if current_user.is_authenticated:
        user = get_user_by_username(current_user.username)

        is_resubmit = False
        old_reddit_comment_id = None
        for result in user_results:
            prev_result = get_event_results_for_user(result.comp_event_id, user)
            if prev_result and prev_result.reddit_comment:
                is_resubmit = True
                old_reddit_comment_id = prev_result.reddit_comment
                break

        try:
            if not is_resubmit:
                url, comment_id = submit_comment_for_user(user, comp_reddit_id, comment_source)
                for result in user_results:
                    result.reddit_comment = comment_id
                    save_event_results_for_user(result, user)
            else:
                url, comment_id = update_comment_for_user(user, old_reddit_comment_id, comment_source)
                for result in user_results:
                    result.reddit_comment = comment_id
                    save_event_results_for_user(result, user)
            return render_template(COMMENT_SUCCESS_TEMPLATE, comment_url=url,
                                   current_competition=comp)
        except Exception as e:
            import sys
            print(e, file=sys.stderr)
            return render_template(COMMENT_FAILURE_TEMPLATE, comment_source=comment_source,
                                   comp_url=comp_thread_url, current_competition=comp)

    # show comment source page
    return render_template(COMMENT_SOURCE_TEMPLATE, comment_source=comment_source,
                           comp_url=comp_thread_url, current_competition=comp)
