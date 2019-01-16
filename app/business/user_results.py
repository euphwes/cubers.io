""" Methods for processing UserEventResults. """

from sys import maxsize as MAX

from arrow import now

from app import CUBERS_APP
from app.persistence.comp_manager import get_comp_event_by_id
from app.persistence.events_manager import get_event_by_name
from app.persistence.user_results_manager import get_pb_single_event_results_except_current_comp,\
    bulk_save_event_results, get_pb_average_event_results_except_current_comp,\
    get_all_complete_user_results_for_user_and_event
from app.persistence.models import UserEventResults, UserSolve, EventFormat
from app.util.times_util import convert_centiseconds_to_friendly_time

# -------------------------------------------------------------------------------------------------

# The front-end dictionary keys
COMMENT       = 'comment'
SOLVES        = 'scrambles' # Because the solve times are paired with the scrambles in the front end
TIME          = 'time'
SCRAMBLE_ID   = 'id'
IS_DNF        = 'isDNF'
IS_PLUS_TWO   = 'isPlusTwo'
COMP_EVENT_ID = 'comp_event_id'
NAME          = 'name'

# Other useful constant values
FMC          = 'FMC'
DNF          = 'DNF'
BLIND_EVENTS = ('2BLD', '3BLD', '4BLD', '5BLD')

# Auto-blacklist notes
_AUTO_NOTE_TEMPLATE = "Results automatically hidden on {date} because the {type} is less than the "
_AUTO_NOTE_TEMPLATE += "'{factor} * WR {type}' threshold for this event."

SINGLE  = 'single'
AVERAGE = 'average'

# -------------------------------------------------------------------------------------------------

def build_user_event_results(user_events_dict, user):
    """ Builds a UserEventsResult object from a dictionary coming in from the front-end, which
    contains the competition event ID and the user's solves paired with the scrambles. """

    # This dictionary just has one key/value pair, get the relevant info out of it
    comp_event_id   = list(user_events_dict.keys())[0]
    comp_event_dict = user_events_dict[comp_event_id]
    comment = comp_event_dict.get(COMMENT, '')

    # Retrieve the CompetitionEvent from the DB and get the event name, format, and expected solves
    comp_event          = get_comp_event_by_id(comp_event_id)
    event_id            = comp_event.Event.id
    event_name          = comp_event.Event.name
    event_format        = comp_event.Event.eventFormat
    expected_num_solves = comp_event.Event.totalSolves

    # Create the actual UserEventResults
    results = UserEventResults(comp_event_id=comp_event_id, comment=comment)

    # Build up a list of UserSolves, and set those in the as the solves for this UserEventREsults
    solves = build_user_solves(comp_event_dict[SOLVES])
    results.set_solves(solves)

    # Set the best single and overall average for this event
    set_single_and_average(results, expected_num_solves, event_format)

    # Determine if the user has completed their results for this event
    set_is_complete(results, event_format, expected_num_solves)

    # Figure out if this is for an FMC event, for a blind event, or neither
    # Useful for deciding how to represent results to the user
    results.is_fmc = event_name == FMC
    results.is_blind = event_name in BLIND_EVENTS

    if results.is_complete:
        # Set the result (either best single, mean, or average) depending on event format
        results.result = determine_event_result(results.single, results.average, event_format)

        # Store the "times string" so we don't have to recalculate this again later.
        # It's fairly expensive, so doing this for every UserEventResults in the competition slows
        # down the leaderboards noticeably.
        results.times_string = build_times_string(results, event_format)

        # Determine and set if the user set any PBs in this event
        # If there's no user, no need to check PB flags
        if user:
            set_pb_flags(user, results, event_id)

    return results


def build_user_solves(solves_data):
    """ Builds and returns a list of UserSolves from the data coming from the front end. """

    user_solves = list()

    for solve in solves_data:
        time = solve[TIME]

        # If the user hasn't recorded a time for this scramble, then just skip to the next
        if not time:
            continue

        # Set the time (in centiseconds), DNF and +2 status, and the scramble ID for this UserSolve
        time        = int(time)
        dnf         = solve[IS_DNF]
        plus_two    = solve[IS_PLUS_TWO]
        scramble_id = solve[SCRAMBLE_ID]

        user_solve = UserSolve(time=time, is_dnf=dnf, is_plus_two=plus_two, scramble_id=scramble_id)
        user_solves.append(user_solve)

    return user_solves


def set_is_complete(user_event_results, event_format, expected_num_solves):
    """ Determine whether this event is considered complete or not. """

    # All blind events are best-of-3, but ranked by single,
    # so consider those complete if there are any solves complete at all
    if event_format == EventFormat.Bo3:
        user_event_results.is_complete = bool(user_event_results.solves)

    # Other events are complete if all solves have been completed
    else:
        user_event_results.is_complete = len(user_event_results.solves) == expected_num_solves


def set_single_and_average(user_event_results, expected_num_solves, event_format):
    """ Determines and sets the best single and average for the UserEventResults. """

    # If not all the solves have been completed, we only know the single
    if len(user_event_results.solves) < expected_num_solves:
        user_event_results.single  = determine_best_single(user_event_results.solves)
        user_event_results.average = ''

    # Otherwise set the single and average if all solves are done
    else:
        single, average = determine_bests(user_event_results.solves, event_format)
        user_event_results.single  = single
        user_event_results.average = average


def build_event_summary(event, user):
    """ Builds the times summary for the event and returns it.
    Ex. 2:49.46 = 2:53.39, 2:44.87, (2:58.07), 2:50.14, (2:26.52) """

    event_name   = event[NAME]
    event_format = get_event_by_name(event_name).eventFormat

    # Wrap up the events data in the format expected by `build_user_event_results`
    event_data_dict = dict()
    event_data_dict[event[COMP_EVENT_ID]] = event

    # Build up the UserEventResults
    results = build_user_event_results(event_data_dict, user)

    # If the format is Bo1 (best of 1) just return human-friendly representation of the time
    if event_format == EventFormat.Bo1:
        return convert_centiseconds_to_friendly_time(results.single)

    # The time on the left side of the `=` is the best single in a Bo3 event, otherwise it's the
    # overall average for the event
    best = results.single if (event_format == EventFormat.Bo3) else results.average

    # If this isn't FMC, convert to human-friendly time
    if not event_name == FMC:
        best = convert_centiseconds_to_friendly_time(best)

    # If this is FMC, convert the faux centiseconds representation to the number of moves
    # 2833 --> 28.33 moves
    # If the number of moves is an integer, represent it without the trailing ".00"
    # 2800 --> 28 moves, not 28.00 moves
    else:
        best = (best/100)
        if best == int(best):
            best = int(best)

    return "{} = {}".format(best, results.times_string)


def build_times_string(results, event_format, want_list=False):
    """ Builds a list of individual times, with best/worst times in parens if appropriate
    for the given event format. """

    # TODO: comment this more thorougly below

    solves = results.solves

    time_convert = convert_centiseconds_to_friendly_time

    # Bo1 is special, just return the friendly representation of the one time
    if event_format == EventFormat.Bo1:
        return 'DNF' if solves[0].is_dnf else time_convert(solves[0].get_total_time())

    # FMC is special, the 'time' is actually the number of moves, not number of centiseconds
    # so don't convert to "friendly times" because that makes no sense
    if not results.is_fmc:
        friendly_times = [time_convert(solve.get_total_time()) for solve in solves]
    else:
        friendly_times = [str(int(solve.get_total_time() / 100)) for solve in solves]

    for i, solve in enumerate(solves):
        if solve.is_plus_two:
            friendly_times[i] = friendly_times[i] + "+"

    curr_best   = MAX
    curr_worst  = -1
    best_index  = -1
    worst_index = -1

    dnf_indicies   = list()
    have_found_dnf = False

    for i, solve in enumerate(solves):
        if (not solve.is_dnf) and (solve.get_total_time() < curr_best):
            best_index = i
            curr_best  = solve.get_total_time()

        if (not have_found_dnf) and (solve.get_total_time() > curr_worst):
            worst_index = i
            curr_worst  = solve.get_total_time()

        if solve.is_dnf:
            if not have_found_dnf:
                worst_index = i
                have_found_dnf = True
            dnf_indicies.append(i)

    for i in dnf_indicies:
        if results.is_blind:
            friendly_times[i] = 'DNF(' + friendly_times[i] + ')'
        else:
            friendly_times[i] = 'DNF'

    if event_format == EventFormat.Bo3:
        while len(friendly_times) < 3:
            friendly_times.append('DNS')

    if event_format in [EventFormat.Bo3, EventFormat.Mo3]:
        return friendly_times if want_list else ', '.join(friendly_times)

    friendly_times[best_index] = '({})'.format(friendly_times[best_index])
    friendly_times[worst_index] = '({})'.format(friendly_times[worst_index])

    return friendly_times if want_list else ', '.join(friendly_times)


def determine_if_should_be_autoblacklisted(results):
    """ Determines if this UserEventResults should be auto-blacklisted because of an absurdly low
    time. Uses a multiplicative factor of the current world records as a threshold, which is
    adjustable by environment variable. """

    # If the results aren't complete, don't blacklist yet even if we otherwise would have
    if not results.is_complete:
        return results

    # A multiplicative factor to adjust autoblacklist thresholds up or down, relative to WR
    threshold_factor = CUBERS_APP.config['AUTO_BL_FACTOR']

    # Dictionary of event name to tuple of (WR single, WR average) in centiseconds
    # WCA WRs as of 09 Jan 2019
    # pylint: disable=C0301
    blacklist_thresholds = {
        '2x2':           (49, 121),
        '3x3':           (347, 580),
        '4x4':           (1842, 2113),
        '5x5':           (3728, 4236),
        '6x6':           (7382, 7710),
        '7x7':           (10789, 11163),
        '3BLD':          (1655, 2029),
        '4BLD':          (8641, 1),  # very low dummy average because WCA doesn't track 4BLD WR average
        '5BLD':          (18101, 1), # very low dummy average because WCA doesn't track 5BLD WR average
        'Square-1':      (00, 00),
        'Clock':         (340, 456),
        '3x3OH':         (688, 942),
        'Pyraminx':      (91, 187),
        'Megaminx':      (2781, 3203),
        'Skewb':         (110, 203),
        'FMC':           (1800, 2400),  # in "centi-moves"
        '3x3 With Feet': (1696, 2222)
    }

    # Retrieve the WR thresholds tuple by event name
    comp_event = get_comp_event_by_id(results.comp_event_id)
    thresholds = blacklist_thresholds.get(comp_event.Event.name, None)

    # If we don't have any thresholds for the event, no chance of auto-blacklist
    if not thresholds:
        return results

    wr_single, wr_average = thresholds

    # Check if the result's single should cause this to be auto-blacklisted
    try:
        # If the single is too low, set the blacklisted flag and note,
        # and unset any PB flags which were probably set earlier when
        # build the UserEventResults
        if int(results.single) <= (threshold_factor * wr_single):
            timestamp = now().format('YYYY-MM-DD')
            note = _AUTO_NOTE_TEMPLATE.format(type=SINGLE, date=timestamp, factor=threshold_factor)
            results.blacklist_note = note
            results.is_blacklisted = True
            results.was_pb_average = False
            results.was_pb_single  = False
            return results
    except ValueError:
        pass # int() failed, probably because the single is a DNF

    # Check if the result's average should cause this to be auto-blacklisted
    try:
        # If the average is too low, set the blacklisted flag and note,
        # and unset any PB flags which were probably set earlier when
        # build the UserEventResults
        if int(results.average) <= (threshold_factor * wr_average):
            timestamp = now().format('YYYY-MM-DD')
            note = _AUTO_NOTE_TEMPLATE.format(type=AVERAGE, date=timestamp, factor=threshold_factor)
            results.blacklist_note = note
            results.is_blacklisted = True
            results.was_pb_average = False
            results.was_pb_single  = False
            return results
    except ValueError:
        pass # int() failed, probably because the average is a DNF

    return results

# -------------------------------------------------------------------------------------------------
#                  Stuff related to processing PBs (personal bests) below
# -------------------------------------------------------------------------------------------------

# Some representations of DNF and <no PBs yet>
# A DNF is a PB if no other PBs have been set, so `PB_DNF` is represented as a really slow time
# that's at faster than `NO_PB_YET`.

PB_DNF    = 88888888  # In centiseconds, this is ~246 hours. Slower than any conceivable real time
NO_PB_YET = 99999999

def __pb_representation(time):
    """ Takes a `time` value from a user solve and converts it into a representation useful for
    determining PBs. If a time is recorded, return the centiseconds, otherwise use the contants
    set above. """

    if time == "DNF":
        return PB_DNF
    elif time == '':
        return NO_PB_YET
    else:
        return int(time)


def set_pb_flags(user, event_result, event_id):
    """ Sets the appropriate flag if either the single or average for this event is a PB. """

    pb_single, pb_average = get_pbs_for_user_and_event_excluding_latest(user.id, event_id)

    # If the current single or average are tied with, or faster than, the user's current PB,
    # then flag this result as a PB. Tied PBs count as PBs in WCA rules
    event_result.was_pb_single = __pb_representation(event_result.single) <= pb_single
    event_result.was_pb_average = __pb_representation(event_result.average) <= pb_average

    return event_result


def get_pbs_for_user_and_event_excluding_latest(user_id, event_id):
    """ Returns a tuple of PB single and average for this event for the specified user, except
    for the current comp. Excluding the current comp allows for the user to keep updating their
    results for this comp, and the logic determining if this comp has a PB result doesn't include
    this comp itself. """

    results_with_pb_singles = get_pb_single_event_results_except_current_comp(user_id, event_id)
    singles = [__pb_representation(r.single) for r in results_with_pb_singles]
    pb_single = min(singles) if singles else NO_PB_YET

    results_with_pb_averages = get_pb_average_event_results_except_current_comp(user_id, event_id)
    averages = [__pb_representation(r.average) for r in results_with_pb_averages]
    pb_average = min(averages) if averages else NO_PB_YET

    return pb_single, pb_average


def recalculate_user_pbs_for_event(user_id, event_id):
    """ Recalculates PBs for all UserEventResults for the specified user and event. """

    # Get the user's event results for this event. If they don't have any, we can just bail
    results = get_all_complete_user_results_for_user_and_event(user_id, event_id)
    if not results:
        return

    # Store the results to save all at once. More efficient that way
    event_results_to_save_at_end = list()
    event_results_to_save_at_end.extend(results)

    # Start off at the beginning assuming no PBs
    pb_single_so_far  = NO_PB_YET
    pb_average_so_far = NO_PB_YET

    # Iterate over each result from earliest to latest, checking the singles and averages to see
    # if they are faster than the current fastest to date. Update the UserEventResult PB flags
    # as appropriate
    for result in results:

        # If the result is blacklisted, it's not under consideration for PBs.
        # Make sure the PB flags are False and skip to the next result
        if result.is_blacklisted:
            result.was_pb_single  = False
            result.was_pb_average = False
            continue

        current_single  = __pb_representation(result.single)
        current_average = __pb_representation(result.average)

        # If the current single or average are tied with, or faster than, the user's current PB,
        # then flag this result as a PB. Tied PBs count as PBs in WCA rules
        if current_single <= pb_single_so_far:
            pb_single_so_far = current_single
            result.was_pb_single = True
        else:
            result.was_pb_single = False

        if current_average <= pb_average_so_far:
            pb_average_so_far = current_average
            result.was_pb_average = True
        else:
            result.was_pb_average = False

    # Save all the UserEventResults with the modified PB flags
    bulk_save_event_results(event_results_to_save_at_end)

# -------------------------------------------------------------------------------------------------
#    Logic for determining best single and average from a set of solves, for a given EventFormat
# -------------------------------------------------------------------------------------------------

def determine_best_single(solves):
    """ Determines the best single in the set of solves. """

    if all(solve.is_dnf for solve in solves):
        return DNF

    return min(solve.get_total_time() for solve in solves if not solve.is_dnf)


def determine_event_result(single, average_or_mean, event_format):
    """ Returns the correct overall result (either single or average_or_mean)
    based on the event format. """

    results_dict = {
        EventFormat.Ao5: average_or_mean,
        EventFormat.Mo3: average_or_mean,
        EventFormat.Bo3: single,
        EventFormat.Bo1: single,
    }

    try:
        return results_dict[event_format]
    except KeyError:
        raise ValueError(event_format, '{event_format} is not a valid event format.')


def determine_bests(solves, event_format):
    """ Returns a tuple of (best single, average) for these solves based on the supplied
    event format." """

    bests_func_dict = {
        EventFormat.Ao5: determine_bests_ao5,
        EventFormat.Mo3: determine_bests_mo3,
        EventFormat.Bo3: determine_bests_bo3,
        EventFormat.Bo1: determine_bests_bo1,
    }

    try:
        return bests_func_dict[event_format](solves)
    except KeyError:
        raise ValueError(event_format, '{event_format} is not a valid event format.')


def determine_bests_bo1(solves):
    """ Returns just the one single. """

    solve = solves[0]

    if solve.is_dnf:
        return DNF, ''

    return solve.get_total_time(), ''


def determine_bests_bo3(solves):
    """ Returns the best single for these 3 solves, and 'N/A' for the average. """
    return determine_bests_mo3(solves)


def determine_bests_mo3(solves):
    """ Returns the best single and mean for these 3 solves. """

    dnf_count = sum(1 for solve in solves if solve.is_dnf)

    if dnf_count > 0:
        average = DNF
    else:
        average = int(sum(solve.get_total_time() for solve in solves) / 3.0)

    if dnf_count == 3:
        single = DNF
    else:
        single = min(solve.get_total_time() for solve in solves if not solve.is_dnf)

    return single, average


def determine_bests_ao5(solves):
    """ Returns the best single and average for these 5 solves, where the average
    is the arithmetic mean of the middle 3 solves. """

    dnf_count = sum(1 for solve in solves if solve.is_dnf)

    if dnf_count == 0:
        times   = [solve.get_total_time() for solve in solves]
        best    = min(times)
        worst   = max(times)
        average = int((sum(times) - best - worst) / 3.0)

    elif dnf_count == 1:
        times   = [solve.get_total_time() for solve in solves if not solve.is_dnf]
        best    = min(times)
        average = int((sum(times) - best) / 3.0)

    elif dnf_count == 5:
        average = DNF
        best    = DNF

    else:
        times   = [solve.get_total_time() for solve in solves if not solve.is_dnf]
        average = DNF
        best    = min(times)

    return best, average
