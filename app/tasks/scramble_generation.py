""" Tasks related to pre-generating scrambles for competitions. """

# pylint: disable=line-too-long

from collections import namedtuple

from huey import crontab

from app import CUBERS_APP
from app.persistence.events_manager import get_all_events, add_scrambles_to_scramble_pool
from app.util.events.resources import get_event_resource_for_name, EVENT_COLL

from . import huey
from .admin_notification import notify_admin, AdminNotificationType

# -------------------------------------------------------------------------------------------------

ScramblePoolTopOffInfo = namedtuple('ScramblePoolTopOffInfo', ['event_id', 'event_name', 'num_scrambles'])

# In dev environments, run the task to check the scramble pool every 5 minutes.
# In prod, run it every 6 hours
if CUBERS_APP.config['IS_DEVO']:
    CHECK_SCRAMBLE_POOL_SCHEDULE = crontab(minute="*/5") # Once every 5 minutes
else:
    CHECK_SCRAMBLE_POOL_SCHEDULE = crontab(hour="*/6")   # Once every 6 hours

# -------------------------------------------------------------------------------------------------

@huey.periodic_task(CHECK_SCRAMBLE_POOL_SCHEDULE)
def check_scramble_pool():
    """ A periodic task to check the pre-generated pool of scrambles for all events. If the pool
    is too low for any event, enqueue a task to generate more scrambles for those events. """

    event_scramble_msgs = list()

    for event in get_all_events():

        # Don't pre-generate COLL scrambles. The fact we need a specific COLL each week, and that
        # rotates weekly, makes this more difficult than it needs to be. We'll just generate them
        # on the fly during competition generation, since it's fast anyway
        if event.name == EVENT_COLL.name:
            continue

        # Determine if the scramble pool is too low for this event. If so, enqueue a task to
        # generate enough scrambles for this event to bring the pool up to (2 * number of solves)
        # for that event
        num_missing = (2 * event.totalSolves) - len(event.scramble_pool)
        if num_missing > 0:
            top_off_scramble_pool(ScramblePoolTopOffInfo(event.id, event.name, num_missing))
            event_scramble_msgs.append('{} for {}'.format(num_missing, event.name))

    # No need to notify anybody of anything if no scrambles were generated
    if not event_scramble_msgs:
        return

    title = 'Generating scrambles'
    body  = '\n'.join(event_scramble_msgs)
    notify_admin(title, body, AdminNotificationType.PUSHBULLET_NOTE)


@huey.task()
def top_off_scramble_pool(top_off_info):
    """ A task to generate additional scrambles to add to the pool of pre-generated scrambles for
    various events. """

    event_resource = get_event_resource_for_name(top_off_info.event_name)
    scrambles = [event_resource.get_scramble() for _ in range(top_off_info.num_scrambles)]

    add_scrambles_to_scramble_pool(scrambles, top_off_info.event_id)
