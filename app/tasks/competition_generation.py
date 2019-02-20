""" Tasks related to admin notifications via Pushbullet channels. """

from collections import namedtuple

from arrow import utcnow
from huey import crontab

from app import CUBERS_APP
from app.persistence.comp_manager import get_active_competition
from app.persistence.events_manager import get_all_events, retrieve_from_scramble_pool_for_event,\
    add_scrambles_to_scramble_pool, delete_from_scramble_pool
from app.util.events_resources import get_event_resource_for_name, EVENT_COLL,\
    correct_raw_scramble_for_app

from . import huey
from .admin_notification import notify_admin, AdminNotificationType

# -------------------------------------------------------------------------------------------------

ScramblePoolTopOffInfo = namedtuple('ScramblePoolTopOffInfo', ['event_id', 'event_name', 'n'])
ScramblePoolRepr       = namedtuple('ScramblePoolRepr', ['scramble_reddit', 'scramble_app'])

# Set the schedule for competition-generation related background tasks depending on whether this
# is running in production or in some development environment.

if CUBERS_APP.config['IS_DEVO']:
    print('setting devo schedules')
    CHECK_SCRAMBLE_POOL_SCHEDULE = crontab(minute="*/1")  # Once every 1 minute
    WRAP_WEEKLY_COMP_SCHEDULE    = crontab(minute="*/30") # Once every 30 minutes

else:
    # pylint: disable=line-too-long
    print('setting prod schedules')
    CHECK_SCRAMBLE_POOL_SCHEDULE = crontab(day_of_week='6', hour='4', minute='0') # Sat 4 AM UTC == Fri 11 PM EST
    WRAP_WEEKLY_COMP_SCHEDULE    = crontab(day_of_week='6', hour='3', minute='0') # Sat 3 AM UTC == Fri 10 PM EST

# -------------------------------------------------------------------------------------------------

@huey.periodic_task(WRAP_WEEKLY_COMP_SCHEDULE)
def wrap_weekly_competition():
    """ A periodic task to schedule sub-tasks related to wrapping up the weekly competitions. """

    current_comp = get_active_competition()
    current_time = utcnow().to('US/Eastern').format('hh:mm A dddd, MMMM Do YYYY')

    notification_title = 'Wrapping {}'.format(current_comp.title)
    notification_body  = 'Wrapped at {}'.format(current_time)
    notify_admin(notification_title, notification_body, AdminNotificationType.PUSHBULLET_NOTE)


@huey.periodic_task(CHECK_SCRAMBLE_POOL_SCHEDULE)
def check_scramble_pool():
    """ A periodic task to check the pre-generated pool of scrambles for all events. If the pool
    is too low for any event, enqueue a task to generate more scrambles for those events. """

    for event in get_all_events():

        # Don't pre-generate COLL scrambles. The fact we need a specific COLL each week, and that
        # rotates weekly, makes this more difficult than it needs to be. We'll just generate them
        # on the fly elsewhere
        if event.name == EVENT_COLL.name:
            continue

        # Determine if the scramble pool is too low for this event. If so, enqueue a task to
        # generate enough scrambles for this event to bring the pool up to (2 * number of solves)
        # for that event
        num_missing = (2 * event.totalSolves) - len(event.scramble_pool)
        if num_missing > 0:
            top_off_scramble_pool(ScramblePoolTopOffInfo(event.id, event.name, num_missing))


@huey.task()
def top_off_scramble_pool(top_off_info):
    """ A task to generate additional scrambles to add to the pool of pre-generated scrambles for
    various events. """

    scramble_representations = list()

    event_resource = get_event_resource_for_name(top_off_info.event_name)

    for _ in range(top_off_info.n):
        raw_scramble  = event_resource.get_one_scramble()
        app_scramble  = correct_raw_scramble_for_app(top_off_info.event_name, raw_scramble)
        scramble_repr = ScramblePoolRepr(scramble_app=raw_scramble, scramble_reddit=raw_scramble)
        scramble_representations.append(scramble_repr)

    add_scrambles_to_scramble_pool(scramble_representations, top_off_info.event_id)

    title = 'Scrambles Generated'
    body  = 'Pre-generated {} scrambles for {}'.format(top_off_info.n, top_off_info.event_name)
    notify_admin(title, body, AdminNotificationType.PUSHBULLET_NOTE)
