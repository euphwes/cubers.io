""" Tasks related to pre-generating scrambles for competitions. """

from collections import namedtuple

from huey import crontab  # type: ignore

from cubersio import app
from cubersio.persistence.events_manager import get_all_events, add_scramble_to_scramble_pool
from cubersio.util.events.resources import get_event_definition_for_name, EVENT_COLL, EVENT_FTO, EVENT_REX

from . import huey


ScramblePoolTopOffInfo = namedtuple('ScramblePoolTopOffInfo', ['event_id', 'event_name', 'num_scrambles'])

# In dev environments, run the task to check the scramble pool every minute.
# In prod, run it every 3 hours (frequently enough so that new events get populated with scrambles quickly)
if app.config['IS_DEVO']:
    CHECK_SCRAMBLE_POOL_SCHEDULE = crontab(minute="*/1")
else:
    CHECK_SCRAMBLE_POOL_SCHEDULE = crontab(hour="*/3", minute="0")


@huey.periodic_task(CHECK_SCRAMBLE_POOL_SCHEDULE)
def check_scramble_pool() -> None:
    """ A periodic task to check the pre-generated pool of scrambles for all events. If the pool is too low for any
    event, queue up a task to generate more scrambles for those events. """
    with app.app_context():
        for event in get_all_events():

            # Don't pre-generate COLL scrambles. The fact we need a specific COLL each week, and that rotates weekly,
            # makes this more difficult than it needs to be. We'll just generate them on the fly during competition
            # generation, since it's fast anyway.
            if event.name == EVENT_COLL.name:
                continue

            # Determine if the scramble pool is too low for this event. If so, queue up a task to generate enough scrambles
            # for this event to bring the pool up to (2 * number of solves) for that event.
            num_missing = (2 * event.totalSolves) - len(event.scramble_pool)
            if num_missing > 0:
                top_off_scramble_pool(ScramblePoolTopOffInfo(event.id, event.name, num_missing))


@huey.task()
def top_off_scramble_pool(top_off_info: ScramblePoolTopOffInfo) -> None:
    """ A task to generate additional scrambles to add to the pool of pre-generated scrambles for various events. """
    with app.app_context():
        event_resource = get_event_definition_for_name(top_off_info.event_name)
        if not event_resource:
            raise RuntimeError(f"Can't find an EventResource for event {top_off_info.event_name}")

        if event_resource.name in (EVENT_REX.name, EVENT_FTO.name):
            # FTO and Rex's scramblers return multiple scrambles at once
            scrambles = event_resource.get_multiple_scrambles(top_off_info.num_scrambles)
        else:
            scrambles = [event_resource.get_scramble() for _ in range(top_off_info.num_scrambles)]

        for scramble in scrambles:
            add_scramble_to_scramble_pool(scramble, top_off_info.event_id)
