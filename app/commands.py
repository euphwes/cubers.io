""" Utility Flask commands for administrating the app. """

import click

from app import app
from app.business.user_results.personal_bests import recalculate_user_pbs_for_event
from app.persistence.comp_manager import get_complete_competitions, get_all_comp_events_for_comp,\
    get_competition, override_title_for_next_comp, set_all_events_flag_for_next_comp, get_comp_event_by_id
from app.persistence.events_manager import get_all_events
from app.persistence.user_results_manager import get_event_results_for_user, save_event_results
from app.persistence.user_manager import get_all_users, get_all_admins, set_user_as_admin,\
    unset_user_as_admin, UserDoesNotExistException, set_user_as_results_moderator, unset_user_as_results_moderator,\
    get_user_by_username
from app.business.user_results import set_medals_on_best_event_results
from app.business.user_results.creation import process_event_results
from app.tasks.competition_management import post_results_thread_task,\
    generate_new_competition_task, wrap_weekly_competition, run_user_site_rankings

# -------------------------------------------------------------------------------------------------
# Below are admin commands for creating new competitions, and scoring previous ones
# -------------------------------------------------------------------------------------------------

@app.cli.command()
@click.option('--all_events', is_flag=True, default=False)
def set_all_events_flags(all_events):
    """ Sets the all-events flag next competition. """

    set_all_events_flag_for_next_comp(all_events)


@app.cli.command()
@click.option('--title', '-t', type=str)
def set_title_override(title):
    """ Sets an override title for the next competition. """

    title = title if title else None
    override_title_for_next_comp(title)


@app.cli.command()
@click.option('--all_events', is_flag=True, default=False)
@click.option('--title', '-t', type=str)
def score_and_generate_new_comp(all_events, title):
    """ Scores the previous competition, and generates a new competition. """

    title = title if title else None
    override_title_for_next_comp(title)
    set_all_events_flag_for_next_comp(all_events)

    wrap_weekly_competition()


@app.cli.command()
@click.option('--comp_id', '-i', type=int)
@click.option('--rerun', '-r', is_flag=True, default=False)
def score_comp_only(comp_id, rerun):
    """ Score only the specified competition, optionally as a re-run. """

    comp = get_competition(comp_id)
    post_results_thread_task(comp.id, comp.title, is_rerun=rerun)


@app.cli.command()
@click.option('--all_events', is_flag=True, default=False)
@click.option('--title', '-t', type=str, default=None)
def generate_new_comp_only(all_events, title):
    """ Only generate a new competition, don't score the previous one. """

    title = title if title else None
    override_title_for_next_comp(title)
    set_all_events_flag_for_next_comp(all_events)

    generate_new_competition_task()
    run_user_site_rankings()


@app.cli.command()
def calculate_all_user_site_rankings():
    """ Calculates UserSiteRankings for all users as of the current comp. """

    run_user_site_rankings()

# -------------------------------------------------------------------------------------------------
# Below are admin commands for one-off app administration needs
# -------------------------------------------------------------------------------------------------

@app.cli.command()
@click.option('--username', '-u', type=str)
def set_admin(username):
    """ Sets the specified user as an admin. """

    try:
        set_user_as_admin(username)
    except UserDoesNotExistException as ex:
        print(ex)


@app.cli.command()
@click.option('--username', '-u', type=str)
def remove_admin(username):
    """ Removes admin status for the specified user. """

    try:
        unset_user_as_admin(username)
    except UserDoesNotExistException as ex:
        print(ex)


@app.cli.command()
@click.option('--username', '-u', type=str)
def set_results_mod(username):
    """ Sets the specified user as a results moderator. """

    try:
        set_user_as_results_moderator(username)
    except UserDoesNotExistException as ex:
        print(ex)


@app.cli.command()
@click.option('--username', '-u', type=str)
def remove_results_mod(username):
    """ Removes results moderator status for the specified user. """

    try:
        unset_user_as_results_moderator(username)
    except UserDoesNotExistException as ex:
        print(ex)


@app.cli.command()
def list_admins():
    """ Lists all the admin users. """

    admins = get_all_admins()
    if not admins:
        print('\nNo admins set')
    else:
        print('\nThe following users are admins:')
        for user in get_all_admins():
            print(user.username)


@app.cli.command()
def recalculate_pbs():
    """ Works through every user, every event type, and re-calculates PB averages and singles
    and sets appropriate flags on UserEventResults. """

    all_users = get_all_users()
    user_count = len(all_users)

    all_events = get_all_events()

    for i, user in enumerate(all_users):
        print("\nRecalculating PBs for {} ({}/{})".format(user.username, i + 1, user_count))
        for event in all_events:
            recalculate_user_pbs_for_event(user.id, event.id)

# -------------------------------------------------------------------------------------------------
# Below are utility commands intended to just be one-offs, to backfill or fix broken data
# -------------------------------------------------------------------------------------------------

@app.cli.command()
@click.option('--comp_id', '-i', type=int)
def rerun_podiums_for_comp(comp_id):
    """ Utility command to backfill all UserEventResults for a specific past competitions with
    gold, silver, bronze medal flags. """

    set_medals_on_best_event_results(get_all_comp_events_for_comp(comp_id))


@app.cli.command()
def backfill_results_medals():
    """ Utility command to backfill all UserEventResults for past competitions with
    gold, silver, bronze medal flags. """

    all_comps = get_complete_competitions()
    total_num = len(all_comps)
    for i, comp in enumerate(all_comps):
        print('\nBackfilling for comp {} ({}/{})'.format(comp.id, i + 1, total_num))
        set_medals_on_best_event_results(get_all_comp_events_for_comp(comp.id))


@app.cli.command()
@click.option('--username', '-u', type=str)
@click.option('--comp_event_id', '-i', type=int)
def reprocess_results_for_user_and_comp_event(username, comp_event_id):
    """ Reprocesses the event results for the specified user and competition event. """

    user = get_user_by_username(username)
    if not user:
        print("Oops, that user doesn't exist.")

    comp_event = get_comp_event_by_id(comp_event_id)
    if not comp_event:
        print("Oops, that comp event doesn't exist.")

    results = get_event_results_for_user(comp_event_id, user)
    results = process_event_results(results, comp_event, user)
    save_event_results(results)
