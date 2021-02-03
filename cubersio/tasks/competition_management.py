""" Tasks related to creating and scoring competitions. """

from huey import crontab

from cubersio import app
from cubersio.business.rankings import precalculate_user_site_rankings
from cubersio.business.user_results import set_medals_on_best_event_results
from cubersio.persistence.comp_manager import get_active_competition, get_all_comp_events_for_comp
from cubersio.util.competition.generation import generate_new_competition
from cubersio.util.competition.scoring import post_results_thread
# from app.tasks.gift_code_management import send_gift_code_winner_approval_pm
from cubersio.tasks.reddit import prepare_new_competition_notification,\
    prepare_end_of_competition_info_notifications

from . import huey

# -------------------------------------------------------------------------------------------------

if app.config['IS_DEVO']:
    # don't run as periodic in devo
    WRAP_WEEKLY_COMP_SCHEDULE = lambda _ : False
    RUN_RANKINGS_SCHEDULE = lambda _ : False

else:
    # Run the rankings task several hours after the comp stuff. I think we're having memory issues.
    WRAP_WEEKLY_COMP_SCHEDULE = crontab(day_of_week='1', hour='2', minute='0')
    RUN_RANKINGS_SCHEDULE = crontab(day_of_week='1', hour='6', minute='0')

# -------------------------------------------------------------------------------------------------

@huey.periodic_task(RUN_RANKINGS_SCHEDULE)
def run_weekly_site_rankings():
    """ A periodic task to run the site rankings stuff weekly. """

    run_user_site_rankings()


@huey.task()
def run_user_site_rankings():
    """ A task to run the calculations to update user site rankings based on the latest data. """

    # Let's keep the timing stuff handy, I want to probably send this via Reddit PM later
    # start = utcnow()
    # user_count = get_user_count()
    precalculate_user_site_rankings()
    # end = utcnow()


@huey.periodic_task(WRAP_WEEKLY_COMP_SCHEDULE)
def wrap_weekly_competition():
    """ A periodic task to schedule sub-tasks related to wrapping up the weekly competitions. """

    current_comp = get_active_competition()

    comp_events_in_comp = get_all_comp_events_for_comp(current_comp.id)
    set_medals_on_best_event_results(comp_events_in_comp)

    post_results_thread_task(current_comp.id)
    prepare_end_of_competition_info_notifications(current_comp.id)
    generate_new_competition_task()
    # send_gift_code_winner_approval_pm(current_comp.id)


@huey.task()
def post_results_thread_task(comp_id, is_rerun=False):
    """ A task to score the specified competition's Reddit thread. """

    post_results_thread(comp_id, is_rerun=is_rerun)


@huey.task()
def generate_new_competition_task():
    """ A task to generate a new competition. """

    competition, was_all_events = generate_new_competition()
    prepare_new_competition_notification(competition.id, was_all_events)
