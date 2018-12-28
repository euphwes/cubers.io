""" Utility module for providing access to business logic for user solves. """

from app import DB
from app.persistence.comp_manager import get_comp_event_by_id,\
    get_all_user_results_for_comp_and_user, get_active_competition, get_all_competitions_user_has_participated_in,\
    get_all_events_user_has_participated_in, get_all_complete_user_results_for_comp_and_user
from app.persistence.models import Competition, CompetitionEvent, Event, UserEventResults,\
    User, UserSolve, EventFormat
from app.util.events_util import determine_bests, determine_best_single, determine_event_result
from app.util.reddit_util import build_times_string

from collections import OrderedDict

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
            # split the times string into components, add to a list called
            # "solves_helper" which is used in the UI to show individual solves
            # and make sure the length == 5, filled with empty strings if necessary
            solves_helper = results.times_string.split(', ')
            while len(solves_helper) < 5:
                solves_helper.append('')
            setattr(results, 'solves_helper', solves_helper)

            # store these UserEventResults for this Competition
            event = id_to_events[results.CompetitionEvent.event_id]
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
