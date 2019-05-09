""" Tasks related to admin notifications via Pushbullet channels. """

from os import environ

from arrow import utcnow

from . import huey

from app import app
from app.persistence.comp_manager import get_participants_in_competition, get_competition
from app.persistence.weekly_metrics_manager import get_weekly_metrics

# -------------------------------------------------------------------------------------------------

class AdminNotificationType:
    """ Enum-esque container for encapsulating admin notification types """

    PUSHBULLET_NOTE = 'pb_note'
    PUSHBULLET_LINK = 'pb_link'

# -------------------------------------------------------------------------------------------------

# Get the Pushbullet API key and target channel tag from environment variables
PUSHBULLET_API_KEY        = environ.get('PUSHBULLET_API_KEY', None)
PUSHBULLET_TARGET_CHANNEL = environ.get('PUSHBULLET_TARGET_CHANNEL', None)

# If we have both of those, assume for now we'll be operating with admin notification enabled
PUSHBULLET_ADMIN_NOTIFICATION_ENABLED = bool(PUSHBULLET_API_KEY) and bool(PUSHBULLET_TARGET_CHANNEL)

# If we're missing some Pushbullet setup, log it so we know
if not PUSHBULLET_ADMIN_NOTIFICATION_ENABLED:
    MSG = "Can't set up admin notifications: "
    MSG += "missing one or more of the following environment variables -- "
    MSG += 'PUSHBULLET_API_KEY, PUSHBULLET_TARGET_CHANNEL'
    app.logger.error(MSG)

# Starting with the assumption we'll be able to send notifications over Pushbullet
# instantiate a Pushbullet client and look for the channel specified
if PUSHBULLET_ADMIN_NOTIFICATION_ENABLED:
    from pushbullet import Pushbullet

    CHANNEL = None
    for channel in Pushbullet(PUSHBULLET_API_KEY).channels:
        if channel.channel_tag == PUSHBULLET_TARGET_CHANNEL:
            CHANNEL = channel
            break

    # If we weren't able to find the channel specified, turn off the 'admin notification enabled'
    # flag so our notify_admin function effectively does nothing
    if not CHANNEL:
        PUSHBULLET_ADMIN_NOTIFICATION_ENABLED = False
        MSG = "Can't set up admin notifications: "
        MSG += "couldn't find Pushbullet channel for tag {}".format(PUSHBULLET_TARGET_CHANNEL)
        app.logger.error(MSG)

    # Otherwise if we found the channel, create a map between notification type and functions
    # bound to the Pushbullet channel itself
    else:
        NOTIFICATION_TYPE_ACTIONS = dict({
            AdminNotificationType.PUSHBULLET_NOTE: CHANNEL.push_note,
            AdminNotificationType.PUSHBULLET_LINK: CHANNEL.push_link,
        })

# -------------------------------------------------------------------------------------------------

WEEKLY_REPORT_TITLE_TEMPLATE = 'Weekly report for "{comp_name}"'

WEEKLY_REPORT_BODY_TEMPLATE = """{total_participants} users participated.
{new_users_count} new users registered."""

# -------------------------------------------------------------------------------------------------

@huey.task()
def notify_admin(title, content, notification_type):
    """ Sends an admin notification (note, link, etc) with the content supplied,
    to the target Pushbullet channel specified above. """

    if not PUSHBULLET_ADMIN_NOTIFICATION_ENABLED:
        return

    timestamp = utcnow().to('US/Mountain').format('[YYYY/MM/DD hh:mm:ss A]')
    content = "{}\n{}".format(timestamp, content)

    NOTIFICATION_TYPE_ACTIONS[notification_type](title, content)


@huey.task()
def send_weekly_report(comp_id):
    """ Builds and sends an end-of-week report with stats from the specified competition. """

    metrics = get_weekly_metrics(comp_id)

    new_users_count = metrics.new_users_count if metrics.new_users_count else 0

    title = WEEKLY_REPORT_TITLE_TEMPLATE.format(comp_name=get_competition(comp_id).title)
    content = WEEKLY_REPORT_BODY_TEMPLATE.format(
        total_participants=len(get_participants_in_competition(comp_id)),
        new_users_count=new_users_count,
    )

    notify_admin(title, content, AdminNotificationType.PUSHBULLET_NOTE)
