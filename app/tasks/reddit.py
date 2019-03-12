""" Tasks related to interacting with Reddit. """

from app.persistence.user_results_manager import save_event_results_for_user,\
    get_comment_id_by_comp_id_and_user, get_all_complete_user_results_for_comp_and_user
from app.persistence.comp_manager import get_competition, get_all_comp_events_for_comp
from app.persistence.user_manager import get_user_by_id
from app.persistence.settings_manager import get_all_user_ids_with_setting_value, TRUE_STR,\
    SettingCode
from app.util.reddit import build_comment_source_from_events_results, submit_comment_for_user,\
    update_comment_for_user, send_PM_to_user_with_title_and_body
from app.util.events.resources import get_all_bonus_events_names

from . import huey

# -------------------------------------------------------------------------------------------------

ALL_EVENTS_DESC = """This week we're running a special competition where all events are being
held, including bonus events!"""

ROTATING_EVENTS_DESC = """This week, the bonus events are {bonus_events_list}."""

NEW_COMP_TEMPLATE = """ Hey there {username}, we wanted to let you know that {comp_title} has
been posted at [cubers.io](https://www.cubers.io)!

{bonus_events_desc}"""

NEW_COMP_TITLE = "A new competition has been posted at cubers.io!"

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


@huey.task()
def prepare_new_competition_notification(comp_id, is_all_events):
    """ Builds a new competition notification message, looks up all users who want to receive
    this sort of message, and queues up tasks to send those users PMs. """

    competition = get_competition(comp_id)

    if is_all_events:
        event_desc = ALL_EVENTS_DESC
    else:
        all_events = get_all_comp_events_for_comp(comp_id)
        all_event_names = [event.Event.name for event in all_events]

        all_bonus_event_names = get_all_bonus_events_names()
        bonus_event_names = [name for name in all_event_names if name in all_bonus_event_names]
        bonus_event_names = ", ".join(bonus_event_names[:-1]) + ", and " + bonus_event_names[-1]

        event_desc = ROTATING_EVENTS_DESC.format(bonus_events_list = bonus_event_names)

    for user_id in get_all_user_ids_with_setting_value(SettingCode.REDDIT_COMP_NOTIFY, TRUE_STR):
        username = get_user_by_id(user_id).username
        message_body = NEW_COMP_TEMPLATE.format(comp_title = competition.title,
                                                bonus_events_desc = event_desc, username = username)
        send_competition_notification_pm(username, message_body)


@huey.task()
def send_competition_notification_pm(username, message_body):
    """ Sends a new competition notification PM to the specified user. """

    send_PM_to_user_with_title_and_body(username, NEW_COMP_TITLE, message_body)
