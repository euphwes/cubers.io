""" Tasks related to interacting with Reddit. """

from cubersio.persistence.user_results_manager import get_all_complete_user_results_for_comp_and_user
from cubersio.persistence.comp_manager import get_competition, get_all_comp_events_for_comp,\
    get_reddit_participants_in_competition
from cubersio.persistence.user_manager import get_user_by_id
from cubersio.persistence.settings_manager import get_all_user_ids_with_setting_value, SettingCode,\
    TRUE_STR
from cubersio.util.reddit import send_pm_to_user
from cubersio.util.events.resources import BONUS_EVENTS

from . import huey

# -------------------------------------------------------------------------------------------------

ALL_EVENTS_DESC = """This week we're running a special competition where all events are being
held, including bonus events!"""

ROTATING_EVENTS_DESC = """This week, the bonus events are {bonus_events_list}."""

NEW_COMP_TEMPLATE = """Hey there {username}, we wanted to let you know that {comp_title} has
been posted at [cubers.io](https://www.cubers.io)!

{bonus_events_desc}

{opt_out_info}"""

NEW_COMP_TITLE = "A new competition has been posted at cubers.io!"

# -------------------------------------------------------------------------------------------------

END_OF_COMP_TITLE_TEMPLATE = "Your results for {comp_title}"

END_OF_COMP_BODY_TEMPLATE = """Hi, {username}! Here's your report for {comp_title}.

You participated in {event_count} events, with a total of {solves_count} solves.
{pb_info}{podium_info}

{opt_out_info}

We're looking forward to having you back next week!"""

PB_INFO_TEMPLATE = "\nYou set {maybe_pluralized_pbs}! Your PBs were in the the following events: {pb_events_list}\n"

PODIUM_INFO_TEMPLATE = "\nCongrats, you podiumed this week! {events_medal_list}\n"

OPT_OUT_INFO = """If you'd like to opt out of these weekly PMs at any time, please visit the
[cubers.io settings page](https://www.cubers.io/settings) and turn off the options under the
"Reddit Preferences" section."""

# -------------------------------------------------------------------------------------------------

def naturally_join(values):
    """ Joins an iterable with commas, but with a ", and" before the last element so it reads a bit
    more naturally.

    Ex. [Apple] --> "Apple"
    Ex. [Apple, Pear] --> "Apple and Pear"
    Ex. [Apple, Pear, Banana] --> "Apple, Pear, and Banana"
    """

    if len(values) == 1:
        return values[0]

    if len(values) == 2:
        return "{} and {}".format(values[0], values[1])

    return ", ".join(values[:-1]) + ", and " + values[-1]

# -------------------------------------------------------------------------------------------------

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

        all_bonus_event_names = [e.name for e in BONUS_EVENTS]
        bonus_event_names = [name for name in all_event_names if name in all_bonus_event_names]
        bonus_event_names = naturally_join(bonus_event_names)

        event_desc = ROTATING_EVENTS_DESC.format(bonus_events_list=bonus_event_names)

    for user_id in get_all_user_ids_with_setting_value(SettingCode.REDDIT_COMP_NOTIFY, TRUE_STR):
        reddit_id = get_user_by_id(user_id).reddit_id
        # If the user doesn't have Reddit info, skip them
        if not reddit_id:
            continue

        message_body = NEW_COMP_TEMPLATE.format(comp_title=competition.title,
                                                bonus_events_desc=event_desc, username=reddit_id,
                                                opt_out_info=OPT_OUT_INFO)
        send_competition_notification_pm(reddit_id, message_body)


@huey.task()
def send_competition_notification_pm(username, message_body):
    """ Sends a new competition notification PM to the specified user. """

    send_pm_to_user(username, NEW_COMP_TITLE, message_body)


@huey.task()
def prepare_end_of_competition_info_notifications(comp_id):
    """ Prepares a list of end-of-competition stats and info for users who have both opted in
    and participated in the specified competition. """

    users_in_comp = get_reddit_participants_in_competition(comp_id)
    opted_in = get_all_user_ids_with_setting_value(SettingCode.REDDIT_RESULTS_NOTIFY, TRUE_STR)

    # Make sure we're only sending messages to users who have both participated in the specified
    # competition, and opted in to receive these messages
    user_ids_to_notify = list(set(users_in_comp) & set(opted_in))

    comp_title = get_competition(comp_id).title

    for user_id in user_ids_to_notify:
        send_end_of_competition_message(user_id, comp_id, comp_title)


@huey.task()
def send_end_of_competition_message(user_id, comp_id, comp_title):
    """ Sends a report to the specified user with info about their participation in the
    competition. """

    user = get_user_by_id(user_id)
    all_results = get_all_complete_user_results_for_comp_and_user(comp_id, user_id, include_blacklisted=False)

    total_solves = 0
    events_with_pbs = list()
    events_with_podium = list()
    total_events_participated_in = len(all_results)

    for event_results in all_results:
        if event_results.was_bronze_medal:
            medal_desc = "{} (bronze)".format(event_results.CompetitionEvent.Event.name)
            events_with_podium.append(medal_desc)
        if event_results.was_silver_medal:
            medal_desc = "{} (silver)".format(event_results.CompetitionEvent.Event.name)
            events_with_podium.append(medal_desc)
        if event_results.was_gold_medal:
            medal_desc = "{} (gold)".format(event_results.CompetitionEvent.Event.name)
            events_with_podium.append(medal_desc)
        if event_results.was_pb_average or event_results.was_pb_single:
            events_with_pbs.append(event_results.CompetitionEvent.Event.name)
        total_solves += len(event_results.solves)

    podium_info = ''
    if events_with_podium:
        events_medal_list = naturally_join(events_with_podium)
        podium_info = PODIUM_INFO_TEMPLATE.format(events_medal_list=events_medal_list)

    pb_info = ''
    if events_with_pbs:
        maybe_pluralized_pbs = "some PBs" if len(events_with_pbs) > 1 else "a PB"
        pb_events_list = naturally_join(events_with_pbs)
        pb_info = PB_INFO_TEMPLATE.format(pb_events_list=pb_events_list, maybe_pluralized_pbs=maybe_pluralized_pbs)

    message_body = END_OF_COMP_BODY_TEMPLATE.format(
        username=user.username,
        comp_title=comp_title,
        event_count=total_events_participated_in,
        solves_count=total_solves,
        pb_info=pb_info,
        podium_info=podium_info,
        opt_out_info=OPT_OUT_INFO
    )

    message_title = END_OF_COMP_TITLE_TEMPLATE.format(comp_title=comp_title)

    send_pm_to_user(user.username, message_title, message_body)
