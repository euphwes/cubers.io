""" Tasks related to creating and scoring competitions. """

# pylint: disable=line-too-long

from datetime import datetime
from pytz import timezone

from arrow import utcnow
from huey import crontab

from app import CUBERS_APP
from app.business.rankings import precalculate_user_site_rankings
from app.business.user_results import set_medals_on_best_event_results
from app.persistence.comp_manager import get_active_competition, get_all_comp_events_for_comp
from app.persistence.user_manager import get_user_count
from app.util.competition.generation import generate_new_competition
from app.util.competition.scoring import score_reddit_thread
from app.tasks.reddit import prepare_new_competition_notification,\
    prepare_end_of_competition_info_notifications

from . import huey
from .admin_notification import notify_admin, send_weekly_report, AdminNotificationType

# -------------------------------------------------------------------------------------------------

# Returns whether it's currently DST in the specified timezone.
# Shamelessly taken from an answer here:
# https://stackoverflow.com/questions/19774709/use-python-to-find-out-if-a-timezone-currently-in-daylight-savings-time
# pylint:disable=invalid-name
is_daylight_savings_in = lambda zonename: bool(datetime.now(timezone(zonename)).dst())

if CUBERS_APP.config['IS_DEVO']:
    WRAP_WEEKLY_COMP_SCHEDULE = lambda dt: False # don't run as periodic in devo
else:
    # We want the comps to be posted on at 10 PM US Eastern on Sundays, but we need to specify the
    # crontab time in UTC. Since the relationship between UTC and US/Eastern changes depending on
    # daylight savings time, we need to account for that
    if is_daylight_savings_in('US/Eastern'):
        # Mon 2 AM UTC == Sun 10 PM US/Eastern
        WRAP_WEEKLY_COMP_SCHEDULE = crontab(day_of_week='1', hour='2', minute='0')
    else:
        # Mon 3 AM UTC == Sun 10 PM US/Eastern
        WRAP_WEEKLY_COMP_SCHEDULE = crontab(day_of_week='1', hour='3', minute='0')

# -------------------------------------------------------------------------------------------------

@huey.periodic_task(WRAP_WEEKLY_COMP_SCHEDULE)
def wrap_weekly_competition():
    """ A periodic task to schedule sub-tasks related to wrapping up the weekly competitions. """

    current_comp = get_active_competition()
    comp_events_in_comp = get_all_comp_events_for_comp(current_comp.id)
    set_medals_on_best_event_results(comp_events_in_comp)

    score_reddit_thread_task(current_comp.id, current_comp.title)
    generate_new_competition_task()
    send_weekly_report(current_comp.id)
    prepare_end_of_competition_info_notifications(current_comp.id)


@huey.task()
def score_reddit_thread_task(comp_id, comp_title, is_rerun=False):
    """ A task to score the specified competition's Reddit thread. """

    score_reddit_thread(comp_id, is_rerun=is_rerun)

    body = 'Scored Reddit thread for {}'.format(comp_title)
    notify_admin(None, body, AdminNotificationType.PUSHBULLET_NOTE)


@huey.task()
def generate_new_competition_task():
    """ A task to generate a new competition. """

    competition, was_all_events = generate_new_competition()

    body  = "Created '{}' competition".format(competition.title)
    notify_admin(None, body, AdminNotificationType.PUSHBULLET_NOTE)

    run_user_site_rankings()
    prepare_new_competition_notification(competition.id, was_all_events)


@huey.task()
def run_user_site_rankings():
    """ A task to run the calculations to update user site rankings based on the latest data. """

    start = utcnow()
    user_count = get_user_count()
    precalculate_user_site_rankings()
    end   = utcnow()

    body = 'Updated site rankings for {} users in {}s'.format(user_count, (end-start).seconds)
    notify_admin(None, body, AdminNotificationType.PUSHBULLET_NOTE)
