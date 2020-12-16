""" Business logic for determining user site rankings and PBs. """

from datetime import datetime
import json

from ranking import Ranking

from app import app
from app import DB
from app.util.events import get_mbld_total_points, get_mbld_fraction_of_hour_remaining
from app.util.events.pagination import _build_pagination
from app.persistence.models import Competition, CompetitionEvent, Event, UserEventResults, User,\
    UserSiteRankings, EventFormat
from app.persistence.events_manager import get_all_events, get_all_WCA_events
from app.persistence.user_manager import get_all_users
from app.persistence.user_site_rankings_manager import save_or_update_site_rankings_for_user
from app.util.sorting import sort_personal_best_records

# -------------------------------------------------------------------------------------------------
#                   Stuff for pre-calculating user PB records with site rankings
# -------------------------------------------------------------------------------------------------

def precalculate_user_site_rankings():
    """ Precalculate user site rankings for event PBs for all users. """

    all_events = get_all_events()
    wca_events = get_all_WCA_events()

    # Each of these dicts are of the following form:
    #    dict[Event][ordered list of PersonalBestRecords]
    events_pb_singles = dict()
    events_pb_averages = dict()

    for event in all_events:

        # It doesn't make sense to keep COLL records, since it's a single alg that changes weekly
        if event.name == "COLL":
            continue

        # Retrieve the the ordered list of PersonalBestRecords for singles for this event
        ordered_pb_singles = get_ordered_pb_singles_for_event(event.id)

        # If nobody at all has competed in this event, just move on to the next
        if not ordered_pb_singles:
            continue

        events_pb_singles[event] = ordered_pb_singles

        # Retrieve the the ordered list of PersonalBestRecords for averages for this event
        ordered_pb_averages = get_ordered_pb_averages_for_event(event.id)
        events_pb_averages[event] = ordered_pb_averages

    # Iterate through all users to determine their site rankings and PBs
    for user in get_all_users():
        # Calculate site rankings for the user
        # pylint: disable=C0301
        rankings = _calculate_site_rankings_for_user(user.id, events_pb_singles, events_pb_averages, wca_events, all_events)

        # Save to the database
        save_or_update_site_rankings_for_user(user.id, rankings)


# pylint: disable=C0301
def _calculate_site_rankings_for_user(user_id, event_singles_map, event_averages_map, wca_events, all_events):
    """ Returns a dict of the user's PB singles and averages for all events they've participated in,
    as well as their rankings amongst the site's users. Format is:
    dict[event ID][(single, single_site_ranking, average, average_site_ranking)] """

    user_rankings_data = OrderedDict()

    # Get the IDs of the WCA events in a set, to make lookup fast later when accumulating sums
    # for the various sum of ranks status
    wca_event_ids = set(e.id for e in wca_events)

    # Start off all sum of ranks stats at 0
    # [single, average]
    sor_all     = [0, 0]
    sor_wca     = [0, 0]
    sor_non_wca = [0, 0]

    # Create the actual UserSiteRankings object to stick the data in when we're done
    user_site_rankings = UserSiteRankings()

    # Hold site-wide Kinchrank (for WCA-only, non-WCA-only, and all events) for this user
    overall_kinchranks = list()
    wca_kinchranks     = list()
    non_wca_kinchranks = list()

    for event in all_events:
        pb_single    = ''
        single_rank  = ''
        pb_average   = ''
        average_rank = ''
        event_kinch  = 0

        event_is_wca = event.id in wca_event_ids

        # It doesn't make sense to keep COLL records, since it's a single alg that changes weekly
        if event.name == "COLL":
            continue

        # Get the lists ranked singles and averages for the current event. If there's nothing
        # in the map for that event, nobody has competed in it yet, so we can skip to the next.
        ranked_singles = event_singles_map.get(event, None)
        if not ranked_singles:
            continue
        ranked_averages = event_averages_map[event]

        # See if there's a result for our user in the singles
        for personal_best in ranked_singles:
            if personal_best.user_id == user_id:
                pb_single   = personal_best.personal_best
                single_rank = personal_best.numerical_rank
                break

        # If our user has no single for this event, their site ranking is
        # (1 + total number of people with a rank for this event)
        if not pb_single:
            single_rank = len(ranked_singles) + 1

        # See if there's a result for our user in the averages. It's ok if there isn't, either
        # because the user doesn't have an average or this event doesn't have averages. we'll just
        # record blank values
        for personal_best in ranked_averages:
            if personal_best.user_id == user_id:
                pb_average   = personal_best.personal_best
                average_rank = personal_best.numerical_rank
                break

        # If our user has no average for this event, their site ranking is
        # (1 + total number of people with a rank for this event)
        if not pb_single:
            average_rank = len(ranked_averages) + 1

        # Determine Kinchrank component for this event
        # TODO: add explanations below
        if event.name == 'MBLD':
            best_mbld = int(ranked_singles[0].personal_best)
            baseline_mbld = get_mbld_total_points(best_mbld) + get_mbld_fraction_of_hour_remaining(best_mbld)
            if pb_single and pb_single != 'DNF':
                coded_mbld = int(pb_single)
                this_mbld  = get_mbld_total_points(coded_mbld) + get_mbld_fraction_of_hour_remaining(coded_mbld)
                event_kinch = round((this_mbld / baseline_mbld) * 100, 3)
        elif event.name in ('FMC', '3BLD'):
            single_kinch = 0
            average_kinch = 0
            if pb_single and pb_single != 'DNF':
                single_kinch = round(int(ranked_singles[0].personal_best) / int(pb_single) * 100, 3)
            if pb_average and pb_average != 'DNF':
                average_kinch = round(int(ranked_averages[0].personal_best) / int(pb_average) * 100, 3)
            event_kinch = max([single_kinch, average_kinch])
        elif event.eventFormat in (EventFormat.Bo1, EventFormat.Bo3):
            if pb_single and pb_single != 'DNF':
                event_kinch = round(int(ranked_singles[0].personal_best) / int(pb_single) * 100, 3)
        else:
            if pb_average and pb_average != 'DNF':
                event_kinch = round(int(ranked_averages[0].personal_best) / int(pb_average) * 100, 3)

        # Accumulate Kinchranks
        overall_kinchranks.append(event_kinch)
        if event_is_wca:
            wca_kinchranks.append(event_kinch)
        else:
            non_wca_kinchranks.append(event_kinch)

        # Records the user's rankings, PBs, and Kinchrank component for this event
        user_rankings_data[event.id] = (pb_single, single_rank, pb_average, average_rank, format(event_kinch, '.3f'))

        # Accumulate sum of ranks
        sor_all[0] += single_rank
        sor_all[1] += average_rank if average_rank else 0
        if event_is_wca:
            sor_wca[0] += single_rank
            sor_wca[1] += average_rank if average_rank else 0
        else:
            sor_non_wca[0] += single_rank
            sor_non_wca[1] += average_rank if average_rank else 0

    # Save the event site rankings data as serialized json into the UserSiteRankigns
    # Set values for Sum Of Ranks, single and average, for combined, WCA, and non-WCA
    # Set values for Kinchranks, for combined, WCA, and non-WCA
    user_site_rankings.data                = json.dumps(user_rankings_data)
    user_site_rankings.timestamp           = datetime.now()
    user_site_rankings.sum_all_single      = sor_all[0]
    user_site_rankings.sum_all_average     = sor_all[1]
    user_site_rankings.sum_wca_single      = sor_wca[0]
    user_site_rankings.sum_wca_average     = sor_wca[1]
    user_site_rankings.sum_non_wca_single  = sor_non_wca[0]
    user_site_rankings.sum_non_wca_average = sor_non_wca[1]

    if overall_kinchranks:
        user_site_rankings.all_kinchrank = round(sum(overall_kinchranks) / (len(overall_kinchranks) + 0.0), 3)
    else:
        user_site_rankings.all_kinchrank = 0

    if wca_kinchranks:
        user_site_rankings.wca_kinchrank = round(sum(wca_kinchranks) / (len(wca_kinchranks) + 0.0), 3)
    else:
        user_site_rankings.wca_kinchrank = 0

    if non_wca_kinchranks:
        user_site_rankings.non_wca_kinchrank = round(sum(non_wca_kinchranks) / (len(non_wca_kinchranks) + 0.0), 3)
    else:
        user_site_rankings.non_wca_kinchrank = 0

    return user_site_rankings

# -------------------------------------------------------------------------------------------------
#                        Stuff for retrieving ordered lists of PB records
# -------------------------------------------------------------------------------------------------

# We don't wan't to use a dictionary here, that defeats the purpose of developer-readable objects.
# Can't use a namedtuple, because the values set there are immutable, and we need to be able to modify the rank,
# which isn't known until after these records are created.
class PersonalBestRecord():
    """ Propery bag class for encapsulating a user's PB record. """

    # pylint: disable=R0913
    def __init__(self, **kwargs):
        self.user_id          = kwargs.get('user_id')
        self.comp_id          = kwargs.get('comp_id')
        self.username         = kwargs.get('username')
        self.comp_title       = kwargs.get('comp_title')
        self.personal_best    = kwargs.get('personal_best')
        self.comment          = kwargs.get('comment')
        self.user_is_verified = kwargs.get('user_is_verified')
        self.rank             = '-1'
        self.numerical_rank   = '-1'


def _build_PersonalBestRecord(record):
    """ Builds a PersonalBestRecord from the 5-tuple returned from the ordered PB queries below.
    The tuple looks like (user_id, single/average, comp_id, comp_title, username). """

    return PersonalBestRecord(
        personal_best=record.single,
        user_id=record.user_id,
        username=record.username,
        comp_id=record.id,
        comp_title=record.title,
        comment=record.comment,
        user_is_verified=record.is_verified
    )


def _filter_one_pb_per_user(personal_bests):
    """ Filters the incoming list of PersonalBestRecords so there's just one per user.
    It's assumed that the first record for each user is the fastest (which is what we want)
    since the queries should order the UserEventResults in descending id order. """

    found_users = set()
    filtered_pbs = list()

    for personal_best in personal_bests:
        if personal_best.user_id in found_users:
            continue
        found_users.add(personal_best.user_id)
        filtered_pbs.append(personal_best)

    return filtered_pbs


def _determine_ranks(personal_bests):
    """ Takes an ordered list of PersonalBestRecords and assigns each PersonalBestRecord a rank.
    Ranks are the same for PersonalBestRecords with identical times.
    Ex: [12, 13, 14, 14, 15] would have ranks [1, 2, 3, 3, 5] """

    # If `personal_bests` is empty, we can't use the ranking mechanism below, so just return
    # the empty list
    if not personal_bests:
        return personal_bests

    # Build a list of just the time values of the personal bests, to be fed into the ranking
    # mechanism. If the PB time value cannot be interpreted as an int, it's probably a DNF so
    # just pretend it's some humongous value which would sorted at the end
    times_values = list()
    for personal_best in personal_bests:
        try:
            times_values.append(int(personal_best.personal_best))
        except ValueError:
            times_values.append(9999999999999)

    # Rank the list of times. The result from this is (rank, time value) where the index
    # of the element for each time value doesn't change from the input to the output
    ranked_times = list(Ranking(times_values, start=1, reverse=True))

    # Give each PersonalBestRecord its rank from the corresponding element in ranked_times
    ranks_seen = set()
    for i, personal_best in enumerate(personal_bests):
        rank = ranked_times[i][0]
        if rank not in ranks_seen:
            ranks_seen.add(rank)
            personal_best.rank = rank
            personal_best.numerical_rank = rank
        else:
            personal_best.rank = ''
            personal_best.numerical_rank = rank

    return personal_bests


def get_ordered_pb_singles_for_event(event_id, event_name, page_number):
    """ Gets a list of PersonalBestRecords, comprised of the fastest single which doesn't belong to
    a blacklisted result, one per user, for the specified event, sorted by single value. """

    # pylint: disable=C0301
    results = DB.session.\
        query(UserEventResults).\
        join(User).\
        join(CompetitionEvent).\
        join(Event).\
        join(Competition).\
        filter(Event.id == event_id).\
        filter(UserEventResults.is_complete).\
        filter(UserEventResults.was_pb_single).\
        filter(UserEventResults.is_blacklisted.isnot(True)).\
        group_by(UserEventResults.id, UserEventResults.user_id, UserEventResults.single, Competition.id, Competition.title, User.username, User.is_verified).\
        order_by(UserEventResults.id.desc()).\
        paginate(page_number, app.config['EVENT_ROUTE_PAGE_SIZE'], error_out=False)
    # pylint: enable=C0301

    pagination = _build_pagination(results, event_name)

    # NOTE: if adding anything to this tuple being selected in values(...) above, add it to the
    # end so that code indexing this tuple doesn't get all jacked. Make sure to make an identical
    # addition to `get_ordered_pb_averages_for_event` and update `_build_PersonalBestRecord`

    personal_bests = [_build_PersonalBestRecord(result) for result in results.items]
    personal_bests = _filter_one_pb_per_user(personal_bests)
    personal_bests.sort(key=sort_personal_best_records)
    personal_bests = _determine_ranks(personal_bests)

    return personal_bests, pagination


def get_ordered_pb_averages_for_event(event_id, page_number):
    """ Gets a list of PersonalBestRecords, comprised of the fastest average which doesn't belong to
    a blacklisted result, one per user, for the specified event, sorted by average value.  """

    # pylint: disable=C0301
    results = DB.session.\
        query(UserEventResults).\
        join(User).\
        join(CompetitionEvent).\
        join(Event).\
        join(Competition).\
        filter(Event.id == event_id).\
        filter(UserEventResults.is_complete).\
        filter(UserEventResults.was_pb_average).\
        filter(UserEventResults.is_blacklisted.isnot(True)).\
        group_by(UserEventResults.id, UserEventResults.user_id, UserEventResults.average, Competition.id, Competition.title, User.username, User.is_verified).\
        order_by(UserEventResults.id.desc()).\
        paginate(page_number, app.config['EVENT_ROUTE_PAGE_SIZE'], error_out=False)
    # pylint: enable=C0301

    # NOTE: if adding anything to this tuple being selected in values(...) above, add it to the
    # end so that code indexing this tuple doesn't get all jacked. Make sure to make an identical
    # addition to `get_ordered_pb_singles_for_event` and update `_build_PersonalBestRecord`

    personal_bests = [_build_PersonalBestRecord(result) for result in results.items]

    # Some events don't have averages, so it's ok to just return an empty list. Checking here
    # instead of checking `results` above, because `results` is a generator and the contents have't
    # been iterated yet
    if not personal_bests:
        return list()

    personal_bests = _filter_one_pb_per_user(personal_bests)
    personal_bests.sort(key=sort_personal_best_records)
    personal_bests = _determine_ranks(personal_bests)

    return personal_bests
