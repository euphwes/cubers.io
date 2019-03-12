""" Tasks related to interacting with Reddit. """

from app.persistence.user_results_manager import save_event_results_for_user,\
    get_comment_id_by_comp_id_and_user, get_all_complete_user_results_for_comp_and_user
from app.persistence.comp_manager import get_competition
from app.persistence.user_manager import get_user_by_id
from app.util.reddit import build_comment_source_from_events_results, submit_comment_for_user,\
    update_comment_for_user

from . import huey

# -------------------------------------------------------------------------------------------------

@huey.task()
def submit_reddit_comment(comp_id, user_id, profile_url):
    """ Task to submit a new, or updating an existing, Reddit comment. """

    user = get_user_by_id(user_id)

    comp = get_competition(comp_id)
    reddit_thread_id = comp.reddit_thread_id
    results = get_all_complete_user_results_for_comp_and_user(comp.id, user_id)
    comment_source = build_comment_source_from_events_results(results, profile_url)

    previous_comment_id = get_comment_id_by_comp_id_and_user(comp.id, user_id)

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


@huey.task(comp_id, is_all_events)
def prepare_new_competition_notification():
    """ Builds a new competition notification message, looks up all users who want to receive
    this sort of message, and queues up tasks to send those users PMs. """

    pass


@huey.task()
def send_competition_notification_pm(user_id, message_body):
    """ Sends a new competition notification PM to the specified user. """

    pass