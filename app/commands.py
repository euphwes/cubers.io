""" Utility Flask commands for administrating the app. """

import click

from app import app
from app.business.user_results.personal_bests import recalculate_user_pbs_for_event
from app.business.user_results.creation import __determine_best_single,\
    __determine_bests, __determine_event_result, __build_times_string
from app.persistence.models import EventFormat
from app.persistence.comp_manager import get_all_competitions, get_complete_competitions,\
    bulk_update_comps, get_all_comp_events_for_comp, get_competition, override_title_for_next_comp,\
    set_all_events_flag_for_next_comp
from app.persistence.events_manager import get_all_events
from app.persistence.user_manager import get_all_users, get_all_admins, set_user_as_admin,\
    unset_user_as_admin, UserDoesNotExistException, set_user_as_results_moderator, unset_user_as_results_moderator
from app.persistence.user_results_manager import get_all_null_is_complete_event_results,\
    get_all_na_average_event_results, save_event_results_for_user, get_all_complete_event_results,\
    bulk_save_event_results, get_all_fmc_results
from app.business.user_results import set_medals_on_best_event_results
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
def fix_goofy_comp_names():
    """ Updates competition titles from "Cubing Competition 299!" format to "Competition 299" """

    comps_to_be_updated = list()
    for comp in get_all_competitions():
        if not comp.title:
            continue
        previous_title = comp.title
        comp.title = comp.title.replace("Cubing ", "").replace("!", "").replace("  ", " ").strip()
        new_title = comp.title
        print("{} --> {}".format(previous_title, new_title))
        comps_to_be_updated.append(comp)

    bulk_update_comps(comps_to_be_updated)


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
def backfill_results_medals():
    """ Utility command to backfill all UserEventResults for past competitions with
    gold, silver, bronze medal flags. """

    all_comps = get_complete_competitions()
    total_num = len(all_comps)
    for i, comp in enumerate(all_comps):
        print('Backfilling for comp {} ({}/{})'.format(comp.id, i + 1, total_num))
        set_medals_on_best_event_results(get_all_comp_events_for_comp(comp.id))


@app.cli.command()
def fix_user_results_add_result_complete():
    """ Utility command to backfill all UserEventResults with null is_complete value. """

    null_is_complete_results = get_all_null_is_complete_event_results()
    fix_user_event_results(null_is_complete_results)


@app.cli.command()
def fix_user_results_with_na_average():
    """ Utility command to backfill all UserEventResults with N/A average value. """

    na_average_results = get_all_na_average_event_results()
    fix_user_event_results(na_average_results)


@app.cli.command()
def fix_fmc_user_results_with_intended_dnf():
    """ Utility command to fix all UserEventResults for FMC where the user had unrealistically
    high solves, probably intended to be DNFs. """

    results_to_save = list()
    for result in get_all_fmc_results():
        altered_result = False
        for solve in result.solves:
            if solve.time >= 15000 and not solve.is_dnf:
                altered_result = True
                solve.is_dnf = True
        if altered_result:
            result.average = 'DNF'
            result.is_fmc = True
            result.times_string = __build_times_string(result, EventFormat.Mo3)
            results_to_save.append(result)
            print("Fixed FMC results with DNF with ID {}".format(result.id))

    bulk_save_event_results(results_to_save)


@app.cli.command()
def backfill_user_results_time_strings():
    """ Utility command to backfill all UserEventResults with no times_string value. """

    complete_results = get_all_complete_event_results()
    total_to_fix = len(complete_results)
    total_fixed  = 0

    results_to_save = list()
    for results in complete_results:
        event_format = results.CompetitionEvent.Event.eventFormat

        results.times_string = __build_times_string(results, event_format)

        results_to_save.append(results)
        total_fixed += 1

        if len(results_to_save) > 25:
            bulk_save_event_results(results_to_save)
            results_to_save = list()
            print("Fixed {} of {} UserEventResults".format(total_fixed, total_to_fix))

    if results_to_save:
        bulk_save_event_results(results_to_save)
        results_to_save = list()
        print("Fixed {} of {} UserEventResults".format(total_fixed, total_to_fix))


def fix_user_event_results(user_event_results):
    """Fix user event results is_complete, single, average, and result fields. """

    total_to_fix = len(user_event_results)
    total_fixed  = 0

    for results in user_event_results:

        event_format        = results.CompetitionEvent.Event.eventFormat
        expected_num_solves = results.CompetitionEvent.Event.totalSolves

        if len(results.solves) < expected_num_solves:
            results.single = __determine_best_single(results.solves)
            results.average = ''
        else:
            single, average = __determine_bests(results.solves, event_format)
            results.single  = single
            results.average = average

        # Determine whether this event is considered complete or not
        if event_format == EventFormat.Bo3:
            # All blind events are best-of-3, but ranked by single,
            # so consider those complete if there are any solves complete at all
            results.is_complete = bool(results.solves)
        else:
            # Other events are complete if all solves have been completed
            results.is_complete = len(results.solves) == expected_num_solves

        # If complete, set the result (either best single, mean, or average) depending on event format
        if results.is_complete:
            results.result = __determine_event_result(results.single, results.average, event_format)

        save_event_results_for_user(results, results.User)

        total_fixed += 1
        print("Fixed {} of {} UserEventResults".format(total_fixed, total_to_fix))
