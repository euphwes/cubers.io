""" Utility Flask commands for testing the app. """
#pylint: disable=C0103

import uuid
import random
import json
import base64

import click

from app import CUBERS_APP
from app.business.user_results import recalculate_user_pbs_for_event, determine_best_single,\
    determine_bests, determine_event_result
from app.business.rankings import precalculate_user_site_rankings
from app.persistence.models import EventFormat
from app.persistence.comp_manager import save_new_competition, get_active_competition,\
    get_all_competitions, bulk_update_comps
from app.persistence.events_manager import get_event_by_name, get_all_events
from app.persistence.user_manager import get_all_users, get_user_by_username, get_all_admins,\
    set_user_as_admin, unset_user_as_admin, UserDoesNotExistException
from app.persistence.user_results_manager import get_all_null_is_complete_event_results,\
    get_all_na_average_event_results, save_event_results_for_user, get_all_complete_event_results,\
    bulk_save_event_results
from app.util.reddit_util import build_times_string
from app.util.generate_comp import generate_new_competition
from app.util.score_comp import score_previous_competition
from app.routes.home import do_reddit_submit

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.cli.command()
@click.option('--all_events', is_flag=True, default=False)
@click.option('--title', '-t', type=str)
def score_and_generate_new_comp(all_events, title):
    """ Scores the previous competition, and generates a new competition. """

    score_previous_competition()
    generate_new_competition(all_events=all_events, title=title)
    precalculate_user_site_rankings()


@CUBERS_APP.cli.command()
@click.option('--comp_id', '-i', type=int)
@click.option('--rerun', '-r', is_flag=True, default=False)
def score_comp_only(comp_id, rerun):
    """ Score only the specified competition, optionally as a re-run. """

    score_previous_competition(is_rerun=rerun, comp_id=comp_id)


@CUBERS_APP.cli.command()
@click.option('--all_events', is_flag=True, default=False)
@click.option('--title', '-t', type=str, default=None)
def generate_new_comp_only(all_events, title):
    """ Only generate a new competition, don't score the previous one. """

    generate_new_competition(all_events=all_events, title=title)
    precalculate_user_site_rankings()

# -------------------------------------------------------------------------------------------------
# Below are admin commands, for one-off app administration needs
# -------------------------------------------------------------------------------------------------

@CUBERS_APP.cli.command()
@click.option('--username', '-u', type=str)
def set_admin(username):
    """ Sets the specified user as an admin. """

    try:
        set_user_as_admin(username)
    except UserDoesNotExistException as ex:
        print(ex)


@CUBERS_APP.cli.command()
@click.option('--username', '-u', type=str)
def remove_admin(username):
    """ Removes admin status for the specified user. """

    try:
        unset_user_as_admin(username)
    except UserDoesNotExistException as ex:
        print(ex)


@CUBERS_APP.cli.command()
def list_admins():
    """ Lists all the admin users. """

    admins = get_all_admins()
    if not admins:
        print('\nNo admins set')
    else:
        print('\nThe following users are admins:')
        for user in get_all_admins():
            print(user.username)


@CUBERS_APP.cli.command()
def calculate_all_user_site_rankings():
    """ Calculates UserSiteRankings for all users as of the current comp. """

    precalculate_user_site_rankings()


@CUBERS_APP.cli.command()
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


@CUBERS_APP.cli.command()
def recalculate_pbs():
    """ Works through every user, every event type, and re-calculates PB averages and singles
    and sets appropriate flags on UserEventResults. """

    all_users = get_all_users()
    user_count = len(all_users)

    all_events = get_all_events()

    for i, user in enumerate(all_users):
        print("\nRecalculating PBs for {} ({}/{})".format(user.username, i+1, user_count))
        for event in all_events:
            recalculate_user_pbs_for_event(user.id, event.id)

# -------------------------------------------------------------------------------------------------
# Below are utility commands intended to just be one-offs, to backfill or fix broken data
# -------------------------------------------------------------------------------------------------

@CUBERS_APP.cli.command()
@click.option('--username', '-u', type=str)
def submit_reddit_for_user(username):
    """ Submits to Reddit for the specified user, for the current competition. """

    user = get_user_by_username(username)
    if not user:
        print("{} is not a valid user".format(username))
        return

    comp = get_active_competition()

    print("Submitting to Reddit for {}".format(username))
    do_reddit_submit(comp.id, user)
    print("Done")


@CUBERS_APP.cli.command()
def fix_user_results_add_result_complete():
    """ Utility command to backfill all UserEventResults with null is_complete value. """

    null_is_complete_results = get_all_null_is_complete_event_results()
    fix_user_event_results(null_is_complete_results)


@CUBERS_APP.cli.command()
def fix_user_results_with_na_average():
    """ Utility command to backfill all UserEventResults with N/A average value. """

    na_average_results = get_all_na_average_event_results()
    fix_user_event_results(na_average_results)


@CUBERS_APP.cli.command()
def backfill_user_results_time_strings():
    """ Utility command to backfill all UserEventResults with no times_string value. """

    complete_results = get_all_complete_event_results()
    total_to_fix = len(complete_results)
    total_fixed  = 0

    results_to_save = list()
    for results in complete_results:
        event_format = results.CompetitionEvent.Event.eventFormat
        event_name = results.CompetitionEvent.Event.name

        is_fmc = event_name == 'FMC'
        is_blind = event_name in ('2BLD', '3BLD', '4BLD', '5BLD')
        results.times_string = build_times_string(results.solves, event_format, is_fmc, is_blind)

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
            results.single = determine_best_single(results.solves)
            results.average = ''
        else:
            single, average = determine_bests(results.solves, event_format)
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
            results.result = determine_event_result(results.single, results.average, event_format)

        save_event_results_for_user(results, results.User)

        total_fixed += 1
        print("Fixed {} of {} UserEventResults".format(total_fixed, total_to_fix))


# -------------------------------------------------------------------------------------------------
# Utility functions for producing scrambles for specific events
# -------------------------------------------------------------------------------------------------

# pylint: disable=C0411
from pyTwistyScrambler import scrambler222, scrambler333, scrambler444, scrambler555,\
    scrambler666, scrambler777, megaminxScrambler, skewbScrambler, squareOneScrambler,\
    pyraminxScrambler, clockScrambler, cuboidsScrambler


def get_2_3_4_relay_scramble():
    """ Get a single scramble for a 2-3-4 relay event, which consists of individual scrambles
    for 2x2, 3x3, and 4x4. """
    s2 = scrambler222.get_WCA_scramble()
    s3 = scrambler333.get_WCA_scramble()
    s4 = scrambler444.get_WCA_scramble()
    return "2x2: {}\n3x3: {}\n4x4: {}".format(s2, s3, s4)


def get_3_relay_of_3():
    """ Get a single scramble for a 3x3 relay of 3 event, which is 3 individual 3x3 scrambles. """
    scrambles = [scrambler333.get_WCA_scramble() for i in range(3)]
    return "1. {}\n2. {}\n3. {}".format(*scrambles)


def get_COLL_scramble():
    """ Return a 'COLL' scramble, which just calls out a specific COLL to perform. """
    return "COLL E" + str(random.choice(range(1,15)))


EVENTS_HELPER = {
    "3x3":             scrambler333.get_WCA_scramble,
    "2x2":             scrambler222.get_WCA_scramble,
    "4x4":             scrambler444.get_WCA_scramble,
    "5x5":             scrambler555.get_WCA_scramble,
    "6x6":             scrambler666.get_WCA_scramble,
    "7x7":             scrambler777.get_WCA_scramble,
    "3BLD":            scrambler333.get_3BLD_scramble,
    "Square-1":        squareOneScrambler.get_WCA_scramble,
    "Clock":           clockScrambler.get_WCA_scramble,
    "3x3OH":           scrambler333.get_WCA_scramble,
    "Pyraminx":        pyraminxScrambler.get_WCA_scramble,
    "Megaminx":        megaminxScrambler.get_WCA_scramble,
    "Kilominx":        megaminxScrambler.get_WCA_scramble,
    "Skewb":           skewbScrambler.get_WCA_scramble,
    "2GEN":            scrambler333.get_2genRU_scramble,
    "F2L":             scrambler333.get_WCA_scramble,
    "LSE":             scrambler333.get_2genMU_scramble,
    "COLL":            get_COLL_scramble,
    "4x4 OH":          scrambler444.get_WCA_scramble,
    "3x3x4":           cuboidsScrambler.get_3x3x4_scramble,
    "3x3x5":           cuboidsScrambler.get_3x3x5_scramble,
    "3x3x2":           cuboidsScrambler.get_3x3x2_scramble,
    "Void Cube":       scrambler333.get_3BLD_scramble,
    "2-3-4 Relay":     get_2_3_4_relay_scramble,
    "FMC":             scrambler333.get_WCA_scramble,
    "3x3 With Feet":   scrambler333.get_WCA_scramble,
    "3x3 Relay of 3":  get_3_relay_of_3,
    "PLL Time Attack": lambda: "Just do every PLL",
    "3x3 Mirror Blocks/Bump": scrambler333.get_WCA_scramble,
}


# -------------------------------------------------------------------------------------------------
# Below are test comp generation commands, not intended to be used in production
# -------------------------------------------------------------------------------------------------

@CUBERS_APP.cli.command()
@click.option('--title', '-t', type=str)
@click.option('--reddit_id', '-r', type=str, default='')
def create_new_test_comp(title, reddit_id):
    """ Creates a new dummy competition for testing purposes. """

    event_data = []
    for event_name, scrambler in EVENTS_HELPER.items():
        data = dict()
        num_solves = get_event_by_name(event_name).totalSolves
        data['scrambles'] = [scrambler() for _ in range(num_solves)]
        data['name'] = event_name
        event_data.append(data)

    if not reddit_id:
        reddit_id = str(uuid.uuid4()).replace('-','')[:10]

    save_new_competition(title, reddit_id, event_data)


@CUBERS_APP.cli.command()
@click.option('--data', '-d', type=str)
def create_new_test_comp_from_b64_data(data):
    """ Creates a test competition based on the data provided. """

    json_data = base64.b64decode(data).decode()
    data = json.loads(json_data)

    title     = data['title']
    reddit_id = data['reddit_id']
    event_data = [event_info for event_info in data['events']]

    save_new_competition(title, reddit_id, event_data)
