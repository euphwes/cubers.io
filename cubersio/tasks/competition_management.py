""" Tasks related to creating and scoring competitions. """

from huey import crontab

from cubersio import app
from cubersio.business.rankings import calculate_user_site_rankings
from cubersio.business.user_results import set_medals_on_best_event_results
from cubersio.persistence.comp_manager import get_active_competition, get_all_comp_events_for_comp
from cubersio.persistence.events_manager import get_all_events
from cubersio.persistence.user_manager import get_all_users
from cubersio.persistence.user_results_manager import calculate_latest_user_pbs_for_event
from cubersio.business.competition.generation import generate_new_competition
from cubersio.business.competition.scoring import post_results_thread
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
    with app.app_context():
        run_user_site_rankings()


@huey.task()
def run_user_site_rankings():
    """ A task to run the calculations to update user site rankings based on the latest data. """
    with app.app_context():
        # Let's keep the timing stuff handy, I want to probably send this via Reddit PM later
        # start = utcnow()
        # user_count = get_user_count()
        calculate_user_site_rankings()
        # end = utcnow()


@huey.periodic_task(WRAP_WEEKLY_COMP_SCHEDULE)
def wrap_weekly_competition():
    """ A periodic task to schedule sub-tasks related to wrapping up the weekly competitions.
    """

    with app.app_context():
        current_comp = get_active_competition()

        comp_events_in_comp = get_all_comp_events_for_comp(current_comp.id)
        set_medals_on_best_event_results(comp_events_in_comp)

        post_results_thread_task(current_comp.id)
        prepare_end_of_competition_info_notifications(current_comp.id)
        generate_new_competition_task()


@huey.task()
def post_results_thread_task(comp_id, is_rerun=False):
    """ A task to score the specified competition's Reddit thread. """
    with app.app_context():
        post_results_thread(comp_id, is_rerun=is_rerun)


@huey.task()
def generate_new_competition_task():
    """ A task to generate a new competition. """
    with app.app_context():
        competition, was_all_events = generate_new_competition()
        prepare_new_competition_notification(competition.id, was_all_events)


@huey.task()
def update_pbs():
    with app.app_context():
        all_users = get_all_users()
        user_count = len(all_users)

        all_events = get_all_events()

        for i, user in enumerate(all_users):
            print("Calculating latest PBs for {} ({}/{})".format(user.username, i + 1, user_count))
            for event in all_events:
                calculate_latest_user_pbs_for_event(user.id, event.id)
