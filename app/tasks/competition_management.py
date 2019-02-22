""" Tasks related to creating and scoring competitions. """

# pylint: disable=line-too-long

from arrow import utcnow
from huey import crontab

from app import CUBERS_APP
from app.business.rankings import precalculate_user_site_rankings
from app.persistence.comp_manager import get_active_competition
from app.persistence.user_manager import get_user_count
from app.util.competition.generation import generate_new_competition
from app.util.competition.scoring import score_reddit_thread

from . import huey
from .admin_notification import notify_admin, send_weekly_report, AdminNotificationType

# -------------------------------------------------------------------------------------------------

if CUBERS_APP.config['IS_DEVO']:
    WRAP_WEEKLY_COMP_SCHEDULE = lambda dt: False # don't run as periodic in devo
else:
    WRAP_WEEKLY_COMP_SCHEDULE = crontab(day_of_week='1', hour='3', minute='0') # Mon 3 AM UTC == Sun 10 PM EST

# -------------------------------------------------------------------------------------------------

@huey.periodic_task(WRAP_WEEKLY_COMP_SCHEDULE)
def wrap_weekly_competition():
    """ A periodic task to schedule sub-tasks related to wrapping up the weekly competitions. """

    current_comp = get_active_competition()

    score_reddit_thread_task(current_comp)
    generate_new_competition_task()
    send_weekly_report(current_comp.id)


@huey.task()
def score_reddit_thread_task(competition, is_rerun=False):
    """ A task to score the specified competition's Reddit thread. """

    score_reddit_thread(competition.id, is_rerun=is_rerun)

    body = 'Scored Reddit thread for {}'.format(competition.title)
    notify_admin(None, body, AdminNotificationType.PUSHBULLET_NOTE)


@huey.task()
def generate_new_competition_task():
    """ A task to generate a new competition. """

    competition = generate_new_competition()

    body  = "Created '{}' competition".format(competition.title)
    notify_admin(None, body, AdminNotificationType.PUSHBULLET_NOTE)

    run_user_site_rankings()


@huey.task()
def run_user_site_rankings():
    """ A task to run the calculations to update user site rankings based on the latest data. """

    start = utcnow()
    user_count = get_user_count()
    precalculate_user_site_rankings()
    end   = utcnow()

    body = 'Updated site rankings for {} users in {}s'.format(user_count, (end-start).seconds)
    notify_admin(None, body, AdminNotificationType.PUSHBULLET_NOTE)
