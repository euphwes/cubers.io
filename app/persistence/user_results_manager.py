""" Utility module for providing access to business logic for user solves. """

from app import DB
from app.persistence.comp_manager import get_comp_event_by_id,\
    get_all_user_results_for_comp_and_user, get_active_competition, get_all_competitions_user_has_participated_in,\
    get_all_events_user_has_participated_in, get_all_complete_user_results_for_comp_and_user, get_all_events,\
    get_previous_competition
from app.persistence.user_manager import get_comp_userlist_blacklist_map, get_all_users
from app.persistence.models import Competition, CompetitionEvent, Event, UserEventResults,\
    User, UserSolve, EventFormat, Blacklist, UserSiteRankings
from app.util.events_util import determine_bests, determine_best_single, determine_event_result
from app.util.reddit_util import build_times_string

from arrow import utcnow as now
from collections import OrderedDict
import json
from ranking import Ranking

# -------------------------------------------------------------------------------------------------

# TODO factor this out into a shared location or utility
starting_max  = 999999999999
dnf_hack_time = 999999999000

def pb_repr(time):
    if time == "DNF":
        return dnf_hack_time
    elif time == '':
        return starting_max
    else:
        return int(time)


def get_user_competition_history(user):
    """ Returns user competition history in the following format:
    dict[Event][dict[Competition][UserEventResults]] """

    history = OrderedDict()
    id_to_events = dict()

    all_events = get_all_events_user_has_participated_in(user.id)

    # iterate over all competitions checking for results for this user
    all_comps = get_all_competitions_user_has_participated_in(user.id)
    all_comps.reverse()

    for event in all_events:
        history[event] = OrderedDict()
        id_to_events[event.id] = event

    for comp in all_comps:
        for results in get_all_complete_user_results_for_comp_and_user(comp.id, user.id):
            event = id_to_events[results.CompetitionEvent.event_id]

            # COLL isn't really meaningful to keep records for, since it's a single alg that changes weekly
            if event.name == "COLL":
                continue

            # split the times string into components, add to a list called
            # "solves_helper" which is used in the UI to show individual solves
            # and make sure the length == 5, filled with empty strings if necessary
            solves_helper = results.times_string.split(', ')
            while len(solves_helper) < 5:
                solves_helper.append('')
            setattr(results, 'solves_helper', solves_helper)

            # store these UserEventResults for this Competition
            history[event][comp] = results

    filtered_history = OrderedDict()
    for event, comps in history.items():
        if comps.items():
            filtered_history[event] = comps

    return filtered_history


def get_user_participated_competitions_count(user_id):
    """ Returns a count of the number of competitions a user has participated in. """

    return DB.session.\
            query(Competition).\
            join(CompetitionEvent).\
            join(UserEventResults).\
            filter(UserEventResults.is_complete).\
            filter(UserEventResults.user_id == user_id).\
            distinct(Competition.id).\
            count()


def get_user_completed_solves_count(user_id):
    """ Returns a count of the number of solves for completed events for the given user. """

    return DB.session.\
            query(UserSolve).\
            join(UserEventResults).\
            filter(UserEventResults.is_complete).\
            filter(UserEventResults.user_id == user_id).\
            distinct(UserSolve.id).\
            count()


def get_comment_id_by_comp_id_and_user(comp_id, user):
    """ Returns a Reddit comment ID for the specified user and competition id. """
    for result in get_all_user_results_for_comp_and_user(comp_id, user.id):
        if result.reddit_comment:
            return result.reddit_comment
    return None


def are_results_different_than_existing(comp_event_results, user):
    """ Determine if these results are identical to any previous existing results for this user
    and this competition event by comparing their times strings. """

    existing_results = get_event_results_for_user(comp_event_results.comp_event_id, user)
    if not existing_results:
        return True

    if existing_results.times_string != comp_event_results.times_string:
        return True

    return existing_results.comment != comp_event_results.comment


def determine_if_any_pbs(user, event_result):
    comp_event = get_comp_event_by_id(event_result.comp_event_id)
    event_id = comp_event.Event.id

    pb_single, pb_average = get_pbs_for_user_and_event_excluding_latest(user.id, event_id)

    event_result.was_pb_single = pb_repr(event_result.single) < pb_single
    event_result.was_pb_average = pb_repr(event_result.average) < pb_average

    return event_result


def build_all_user_results(user_events_dict):
    """ Builds a list of all UserEventsResult objects, from a dictionary of comp event ID and a
    list of scrambles and associated solve times. (this dict comes from front-end) """

    user_results = list()

    for comp_event_id, comp_event_dict in user_events_dict.items():
        solves = comp_event_dict['scrambles']
        comment = comp_event_dict.get('comment', '')
        event_results = build_user_event_results(comp_event_id, solves, comment)
        user_results.append(event_results)

    return user_results


def build_user_event_results(comp_event_id, solves, comment):
    """ Builds a UserEventsResult object from a competition_event ID and a list of scrambles
    and associated solve times. """

    comp_event = get_comp_event_by_id(comp_event_id)
    expected_num_solves = comp_event.Event.totalSolves
    event_format = comp_event.Event.eventFormat
    event_name = comp_event.Event.name

    results = UserEventResults(comp_event_id=comp_event_id, comment=comment)

    for solve in solves:
        time = solve['time']
        if not time:
            continue

        dnf         = solve['isDNF']
        time        = int(solve['time'])
        plus_two    = solve['isPlusTwo']
        scramble_id = solve['id']

        user_solve = UserSolve(time=time, is_dnf=dnf, is_plus_two=plus_two, scramble_id=scramble_id)
        results.solves.append(user_solve)

    if len(results.solves) < expected_num_solves:
        results.single = determine_best_single(results.solves)
        results.average = ''
    else:
        single, average = determine_bests(results.solves, comp_event.Event.eventFormat)
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
    # Also store the "times string" so we don't have to recalculate this again later, notably slowing down the
    # leaderboards tables.
    if results.is_complete:
        results.result = determine_event_result(results.single, results.average, event_format)
        is_fmc = event_name == 'FMC'
        is_blind = event_name in ('2BLD', '3BLD', '4BLD', '5BLD')
        results.times_string = build_times_string(results.solves, event_format, is_fmc, is_blind)

    return results


def get_event_results_for_user(comp_event_id, user):
    """ Retrieves a UserEventResults for a specific user and competition event. """
    return UserEventResults.query.filter(UserEventResults.user_id == user.id)\
                                 .filter(UserEventResults.comp_event_id == comp_event_id)\
                                 .first()


def get_all_null_is_complete_event_results():
    """ Get all UserEventResults with a null is_complete value. """
    return UserEventResults.query.filter(UserEventResults.is_complete == None).all()


def get_all_na_average_event_results():
    """ Get all UserEventResults. """
    return UserEventResults.query.filter(UserEventResults.average == 'N/A').all()


def get_all_complete_event_results():
    """ Gets all complete event results. """
    return UserEventResults.query.filter(UserEventResults.is_complete).all()


def get_pbs_for_user_and_event_excluding_latest(user_id, event_id):
    """ Returns a tuple of PB single and average for this event for the specified user, except
    for the current comp. Excluding the current comp allows for the user to keep updating their
    results for this comp, and the logic determining if this comp has a PB result doesn't include
    this comp itself. """

    current_comp_id = get_active_competition().id

    results_with_pb_singles = DB.session.\
            query(UserEventResults).\
            join(User).\
            join(CompetitionEvent).\
            join(Competition).\
            join(Event).\
            filter(Event.id == event_id).\
            filter(User.id == user_id).\
            filter(Competition.id != current_comp_id).\
            filter(UserEventResults.was_pb_single).\
            filter(UserEventResults.is_complete).\
            order_by(UserEventResults.id).\
            all()

    singles = [pb_repr(r.single) for r in results_with_pb_singles]

    results_with_pb_averages = DB.session.\
            query(UserEventResults).\
            join(User).\
            join(CompetitionEvent).\
            join(Competition).\
            join(Event).\
            filter(Event.id == event_id).\
            filter(User.id == user_id).\
            filter(Competition.id != current_comp_id).\
            filter(UserEventResults.was_pb_average).\
            filter(UserEventResults.is_complete).\
            order_by(UserEventResults.id).\
            all()

    averages = [pb_repr(r.average) for r in results_with_pb_averages]

    pb_single = min(singles) if singles else starting_max
    pb_average = min(averages) if averages else starting_max

    return pb_single, pb_average


def bulk_save_event_results(results_list):
    """ Save a bunch of results at once. """
    for result in results_list:
        DB.session.add(result)
    DB.session.commit()


def save_event_results_for_user(comp_event_results, user):
    """ Associates a UserEventResults with a specific user and saves it to the database.
    If the user already has an EventResults for this competition, update it instead. """

    # if an existing record exists, update that
    existing_results = get_event_results_for_user(comp_event_results.comp_event_id, user)
    if existing_results:
        return __save_existing_event_results(existing_results, comp_event_results)

    # Otherwise associate the new results with this user and save and commit
    comp_event_results.user_id = user.id
    DB.session.add(comp_event_results)
    DB.session.commit()

    return comp_event_results


def __save_existing_event_results(existing_results, new_results):
    """ Update the existing UserEventResults and UserSolves with the new data. """

    existing_results.single         = new_results.single
    existing_results.average        = new_results.average
    existing_results.result         = new_results.result
    existing_results.comment        = new_results.comment
    existing_results.is_complete    = new_results.is_complete
    existing_results.times_string   = new_results.times_string
    existing_results.was_pb_average = new_results.was_pb_average
    existing_results.was_pb_single  = new_results.was_pb_single

    # Update any existing solves with the data coming in from the new solves
    for old_solve in existing_results.solves:
        found = False
        for new_solve in new_results.solves:
            if old_solve.scramble_id == new_solve.scramble_id:
                found = True
                old_solve.time        = new_solve.time
                old_solve.is_dnf      = new_solve.is_dnf
                old_solve.is_plus_two = new_solve.is_plus_two
        if not found:
            DB.session.delete(old_solve)

    # Determine which of the new solves are actually new and add those to the results record
    old_scramble_ids = [solve.scramble_id for solve in existing_results.solves]
    for new_solve in [s for s in new_results.solves if s.scramble_id not in old_scramble_ids]:
        existing_results.solves.append(new_solve)

    DB.session.commit()
    return existing_results

# -------------------------------------------------------------------------------------------------
#                   Stuff for pre-calculating user PB records with site rankings
# -------------------------------------------------------------------------------------------------

def precalculate_user_site_rankings():
    """ Precalculate user site rankings for event PBs for all users. """

    all_events = get_all_events()
    blacklist_mapping = get_comp_userlist_blacklist_map()
    previous_comp = get_previous_competition()

    # Each of these dicts are of the following form:
    #    dict[Event][(ordered list of PB singles with associated user ID, ranked list of PB singles)]
    # where the ordered list of PB singles contains tuples of the form (user_id, single as string)
    # and the ranked list of PB singles contains tuples of the form (rank, single as int)
    events_PB_singles = dict()
    events_PB_averages = dict()

    for event in all_events:

        # COLL isn't really meaningful to keep records for, since it's a single alg that changes weekly
        if event.name == "COLL":
            continue

        # Retrieve the the list of (user ID, PB single) tuples in order of single
        # and build a ranking of those singles values (identical values are ranked the same),
        # then stick that in the dict for the current event
        ordered_PB_singles = get_ordered_users_pb_singles_for_event(event.id, blacklist_mapping)
        singles_values = list()
        for single in ordered_PB_singles:
            try:
                singles_values.append(int(single[1]))
            except:
                singles_values.append(9999999999999)
        ranked_PB_singles = list(Ranking(singles_values, start=1, reverse=True))
        events_PB_singles[event] = (ordered_PB_singles, ranked_PB_singles)

        # Retrieve the the list of (user ID, PB average) tuples in order of average
        # and build a ranking of those averages values (identical values are ranked the same),
        # then stick that in the dict for the current event
        ordered_PB_averages = get_ordered_users_pb_averages_for_event(event.id, blacklist_mapping)
        averages_values = list()
        for average in ordered_PB_averages:
            try:
                averages_values.append(int(average[1]))
            except:
                averages_values.append(9999999999999)
        ranked_PB_averages = list(Ranking(averages_values, start=1, reverse=True))

        events_PB_averages[event] = (ordered_PB_averages, ranked_PB_averages)

    # Iterate through all users to determine their site rankings and PBs
    for user in get_all_users():

        # Calculate site rankings for the user
        site_rankings = calculate_site_rankings_for_user(user.id, events_PB_singles, events_PB_averages)

        # If the rankings dict contains no entries, the user hasn't competed in anything,
        # or falls into the blacklist for all of their events. Don't bother saving anything
        if not site_rankings.keys():
            continue

        # Save to the database
        save_or_update_site_rankings_for_user(user.id, site_rankings, previous_comp)


def get_site_rankings_for_user(user_id):
    """ Retrieves a UserSiteRankings record for the specified user. """

    return DB.session.\
        query(UserSiteRankings).\
        filter(UserSiteRankings.user_id == user_id).\
        first()


def save_or_update_site_rankings_for_user(user_id, site_rankings, previous_comp):
    """ Create or update a UserSiteRankings record for the specified user. """

    rankings_record = get_site_rankings_for_user(user_id)

    if rankings_record:
        print('Updating UserSiteRankings for user {}'.format(user_id))
        rankings_record.data    = json.dumps(site_rankings)
        rankings_record.comp_id = previous_comp.id

    else:
        print('Creating UserSiteRankings for user {}'.format(user_id))
        rankings_record         = UserSiteRankings()
        rankings_record.data    = json.dumps(site_rankings)
        rankings_record.comp_id = previous_comp.id
        rankings_record.user_id = user_id

    DB.session.add(rankings_record)
    DB.session.commit()


def calculate_site_rankings_for_user(user_id, event_singles_map, event_averages_map):
    """ Returns a dict of the user's PB singles and averages for all events they've
    participated in, as well as their rankings amongst the site's users. Format is:
    dict[Event][(single, single_site_ranking, average, average_site_ranking)] """

    print('Calculating site rankings for user {}'.format(user_id))

    user_rankings = OrderedDict()

    for event in get_all_events_user_has_participated_in(user_id):
        our_user_single_index = -1
        our_user_average_index = -1

        # COLL isn't really meaningful to keep records for, since it's a single alg that changes weekly
        if event.name == "COLL":
            continue

        # get the lists of singles/averages and ranked singles/averages for the current event
        singles, ranked_singles = event_singles_map[event]
        averages, ranked_averages = event_averages_map[event]

        # Iterate through the list of singles, trying to find the one that belongs to our user
        # Once found, record that index (it'll be the same in the ranked list), and the single value
        for i, s in enumerate(singles):
            if s[0] == user_id:
                our_user_single_index = i
                our_user_single = s[1]
                break

        # If we didn't find the index, it must mean the user doesn't have a record in this list. Possibly
        # because they were filtered due to the blacklist? Go ahead and bail and go to the next event
        if our_user_single_index == -1:
            continue

        # Get the single ranking of our user
        user_single_ranking = ranked_singles[our_user_single_index][0]

        if not averages:
            # If the averages list is empty, it's because it's an event that doesn't have averages
            # like the relays, or PLL time attack
            our_user_average = ''
            user_average_ranking = ''
        else:
            # Iterate through the list of averages, trying to find the one that belongs to our user
            # Once found, record that index (it'll be the same in the ranked list), and the average value
            for i, avg in enumerate(averages):
                if avg[0] == user_id:
                    our_user_average_index = i
                    our_user_average = avg[1]
                    break

            # Get the average ranking of our user
            user_average_ranking = ranked_averages[our_user_average_index][0]

        # Records the user's rankings and PBs for this event
        user_rankings[event.id] = (our_user_single, user_single_ranking,\
                                our_user_average, user_average_ranking)

    return user_rankings


def sort_results(val1, val2):
    result1 = val1[1]
    result2 = val2[1]
    if not result1:
        result1 = 100000000
    if not result2:
        result2 = 100000000
    if result1 == 'DNF':
        result1 = 99999999
    if result2 == 'DNF':
        result2 = 99999999
    return int(result1) - int(result2)


def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class comparator:
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return comparator


def get_ordered_users_pb_singles_for_event(event_id, blacklist_mapping):
    """ Gets all users' PB singles for the specified event, ordered by single value. """

    print('Determining site-wide user PB singles for event {}'.format(event_id))

    results = DB.session.\
            query(UserEventResults).\
            join(CompetitionEvent).\
            join(Event).\
            join(Competition).\
            filter(Event.id == event_id).\
            filter(UserEventResults.is_complete).\
            filter(UserEventResults.was_pb_single).\
            group_by(UserEventResults.id, UserEventResults.user_id, UserEventResults.single, Competition.id).\
            order_by(UserEventResults.id.desc()).\
            values(UserEventResults.user_id, UserEventResults.single, Competition.id)

    # NOTE: if adding anything to this tuple being selected in values(...) below, add it to the
    # end so that code already indexing this tuple doesn't get all jacked

    found_users = set()
    filtered_results = list()
    for user_id, single, comp_id in results:
        if user_id in found_users:
            continue
        if comp_id in blacklist_mapping.keys() and user_id in blacklist_mapping[comp_id]:
            continue
        found_users.add(user_id)
        filtered_results.append((user_id, single))

    filtered_results.sort(key=cmp_to_key(sort_results))

    return filtered_results


def get_ordered_users_pb_singles_for_event_for_event_results(event_id, blacklist_mapping):
    """ Gets all users' PB singles for the specified event, ordered by single value. """

    results = DB.session.\
            query(UserEventResults).\
            join(User).\
            join(CompetitionEvent).\
            join(Event).\
            join(Competition).\
            filter(Event.id == event_id).\
            filter(UserEventResults.is_complete).\
            filter(UserEventResults.was_pb_single).\
            group_by(UserEventResults.id, UserEventResults.user_id, UserEventResults.single, Competition.id, Competition.title, User.username).\
            order_by(UserEventResults.id.desc()).\
            values(UserEventResults.user_id, UserEventResults.single, Competition.id, Competition.title, User.username)

    # NOTE: if adding anything to this tuple being selected in values(...) below, add it to the
    # end so that code already indexing this tuple doesn't get all jacked

    found_users = set()
    filtered_results = list()
    for user_id, single, comp_id, comp_name, username in results:
        if user_id in found_users:
            continue
        if comp_id in blacklist_mapping.keys() and user_id in blacklist_mapping[comp_id]:
            continue
        found_users.add(user_id)

        filtered_results.append((user_id, single, comp_id, username, comp_name))

    filtered_results.sort(key=cmp_to_key(sort_results))

    return filtered_results


def get_ordered_users_pb_averages_for_event_for_event_results(event_id, blacklist_mapping):
    """ Gets all users' PB averages for the specified event, ordered by average value. """

    results = DB.session.\
            query(UserEventResults).\
            join(User).\
            join(CompetitionEvent).\
            join(Event).\
            join(Competition).\
            filter(Event.id == event_id).\
            filter(UserEventResults.is_complete).\
            filter(UserEventResults.was_pb_average).\
            group_by(UserEventResults.id, UserEventResults.user_id, UserEventResults.single, Competition.id, Competition.title, User.username).\
            order_by(UserEventResults.id.desc()).\
            values(UserEventResults.user_id, UserEventResults.average, Competition.id, Competition.title, User.username)

    # NOTE: if adding anything to this tuple being selected in values(...) below, add it to the
    # end so that code already indexing this tuple doesn't get all jacked

    found_users = set()
    filtered_results = list()
    for user_id, average, comp_id, comp_name, username in results:
        if user_id in found_users:
            continue
        if comp_id in blacklist_mapping.keys() and user_id in blacklist_mapping[comp_id]:
            continue
        found_users.add(user_id)

        filtered_results.append((user_id, average, comp_id, username, comp_name))

    filtered_results.sort(key=cmp_to_key(sort_results))

    return filtered_results


def get_ordered_users_pb_averages_for_event(event_id, blacklist_mapping):
    """ Gets all users' PB averages for the specified event, ordered by average value. """

    print('Determining site-wide user PB averages for event {}'.format(event_id))

    results = DB.session.\
            query(UserEventResults).\
            join(CompetitionEvent).\
            join(Event).\
            join(Competition).\
            filter(Event.id == event_id).\
            filter(UserEventResults.is_complete).\
            filter(UserEventResults.was_pb_average).\
            group_by(UserEventResults.id, UserEventResults.user_id, UserEventResults.average, Competition.id).\
            order_by(UserEventResults.id.desc()).\
            values(UserEventResults.user_id, UserEventResults.average, Competition.id)

    found_users = set()
    filtered_results = list()
    for user_id, average, comp_id in results:
        if user_id in found_users:
            continue
        if comp_id in blacklist_mapping.keys() and user_id in blacklist_mapping[comp_id]:
            continue
        found_users.add(user_id)
        filtered_results.append((user_id, average))

    filtered_results.sort(key=cmp_to_key(sort_results))

    return filtered_results