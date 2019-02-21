""" Tasks related to admin notifications via Pushbullet channels. """

# pylint: disable=line-too-long

from arrow import utcnow
from huey import crontab

from app import CUBERS_APP
from app.persistence.comp_manager import get_active_competition
from app.util.competition.generation import generate_new_competition
from app.util.competition.scoring import score_reddit_thread

from . import huey
from .admin_notification import notify_admin, AdminNotificationType

# -------------------------------------------------------------------------------------------------

# In dev environments, run the task to check the scramble pool every 5 minutes.
# In prod, run it Sat 3 AM UTC, which is Fri 10 PM EST
if CUBERS_APP.config['IS_DEVO']:
    WRAP_WEEKLY_COMP_SCHEDULE = crontab(minute="*/30") # Once every 30 minutes
else:
    WRAP_WEEKLY_COMP_SCHEDULE = crontab(day_of_week='6', hour='3', minute='0') # Sat 3 AM UTC == Fri 10 PM EST

# -------------------------------------------------------------------------------------------------

@huey.periodic_task(WRAP_WEEKLY_COMP_SCHEDULE)
def wrap_weekly_competition():
    """ A periodic task to schedule sub-tasks related to wrapping up the weekly competitions. """

    score_reddit_thread_task(get_active_competition())
    generate_new_competition_task()


@huey.task()
def score_reddit_thread_task(competition, is_rerun=False):
    """ A task to score the specified competition's Reddit thread. """

    start = utcnow()
    score_reddit_thread(competition.id, is_rerun=is_rerun)
    end   = utcnow()

    title = 'Scored Competition'
    body  = 'Scored Reddit thread for {} in {}s'.format(competition.title, (end-start).seconds)
    notify_admin(title, body, AdminNotificationType.PUSHBULLET_NOTE)


@huey.task()
def generate_new_competition_task():
    """ A task to generate a new competition. """

    start = utcnow()
    competition = generate_new_competition()
    end   = utcnow()

    title = 'New Competition'
    body  = 'Created {} in {}s'.format(competition.title, (end-start).seconds)
    notify_admin(title, body, AdminNotificationType.PUSHBULLET_NOTE)
