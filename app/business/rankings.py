""" Business logic for determining user site rankings and PBs. """

from collections import OrderedDict

from ranking import Ranking

from app import DB
from app.persistence.models import Competition, CompetitionEvent, Event, UserEventResults, User
from app.persistence.comp_manager import get_previous_competition
from app.persistence.events_manager import get_all_events, get_all_events_user_has_participated_in
from app.persistence.user_manager import get_all_users
from app.persistence.user_site_rankings_manager import save_or_update_site_rankings_for_user,\
    update_one_event_site_rankings_for_user

# -------------------------------------------------------------------------------------------------
#                   Stuff for pre-calculating user PB records with site rankings
# -------------------------------------------------------------------------------------------------

def precalculate_site_rankings_for_event(event):
    """ Precalculate user site rankings for just the specified event. """

    # It doesn't make sense to keep COLL records, since it's a single alg that changes weekly
    if event.name == "COLL":
        return

    # Each of these dicts are of the following form:
    #    dict[Event][ordered list of PersonalBestRecords]
    events_pb_singles = dict()
    events_pb_averages = dict()

    # Retrieve the the ordered list of PersonalBestRecords for singles for this event
    ordered_pb_singles = get_ordered_pb_singles_for_event(event.id)

    # If nobody at all has competed in this event, just leave
    if not ordered_pb_singles:
        return

    events_pb_singles[event] = ordered_pb_singles

    # Retrieve the the ordered list of PersonalBestRecords for averages for this event
    ordered_pb_averages = get_ordered_pb_averages_for_event(event.id)
    events_pb_averages[event] = ordered_pb_averages

    # Iterate through all users to determine their site rankings and PBs
    for user in get_all_users():

        # Calculate site rankings for the user for just this event
        rankings = _calculate_site_rankings_for_user(user.id, events_pb_singles,\
            events_pb_averages, event_override=event)

        # If the user hasn't competed in anything, no need to save site rankings.
        if not rankings.keys():
            continue

        # Save to the database
        update_one_event_site_rankings_for_user(user.id, rankings, event)


def precalculate_user_site_rankings():
    """ Precalculate user site rankings for event PBs for all users. """

    all_events = get_all_events()

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
        rankings = _calculate_site_rankings_for_user(user.id, events_pb_singles, events_pb_averages, events_list=all_events)

        # If the user hasn't competed in anything, no need to save site rankings.
        if not rankings.keys():
            continue

        # Save to the database
        save_or_update_site_rankings_for_user(user.id, rankings)


# pylint: disable=C0301
def _calculate_site_rankings_for_user(user_id, event_singles_map, event_averages_map, event_override=None, events_list=None):
    """ Returns a dict of the user's PB singles and averages for all events they've participated in,
    as well as their rankings amongst the site's users. Format is:
    dict[event ID][(single, single_site_ranking, average, average_site_ranking)] """

    user_rankings = OrderedDict()

    # If an event_override is specified, only calculate rankings for that specific event
    if event_override:
        events_to_consider = [event_override]

    # Otherwise work through all events for this user
    else:
        events_to_consider = events_list if events_list else get_all_events()

    for event in events_to_consider:
        pb_single    = ''
        single_rank  = ''
        pb_average   = ''
        average_rank = ''

        # It doesn't make sense to keep COLL records, since it's a single alg that changes weekly
        if event.name == "COLL":
            continue

        # get the lists ranked singles and averages for the current event
        ranked_singles = event_singles_map[event]
        ranked_averages = event_averages_map[event]

        # See if there's a result for our user in the singles
        for personal_best in ranked_singles:
            if personal_best.user_id == user_id:
                pb_single   = personal_best.personal_best
                single_rank = personal_best.rank
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
                average_rank = personal_best.rank
                break

        # If our user has no average for this event, their site ranking is
        # (1 + total number of people with a rank for this event)
        if not pb_single:
            average_rank = len(ranked_averages) + 1

        # Records the user's rankings and PBs for this event
        user_rankings[event.id] = (pb_single, single_rank, pb_average, average_rank)

    return user_rankings


# -------------------------------------------------------------------------------------------------
#                        Stuff for retrieving ordered lists of PB records
# -------------------------------------------------------------------------------------------------

# We don't wan't to use a dictionary here, that defeats the purpose of developer-readable objects
# Can't use a namedtuple, because the values set there are immutable, and we need to be able to
# modify the rank, which isn't known until after these records are created.
#
# pylint: disable=R0903
class PersonalBestRecord():
    """ Propery bag class for encapsulating a user's PB record. """

    # pylint: disable=R0913
    def __init__(self, **kwargs):
        self.user_id       = kwargs.get('user_id')
        self.comp_id       = kwargs.get('comp_id')
        self.username      = kwargs.get('username')
        self.comp_title    = kwargs.get('comp_title')
        self.personal_best = kwargs.get('personal_best')
        self.rank          = '-1'


# pylint: disable=C0103
def _build_PersonalBestRecord(query_tuple):
    """ Builds a PersonalBestRecord from the 5-tuple returned from the ordered PB queries below.
    The tuple looks like (user_id, single/average, comp_id, comp_title, username). """

    user_id, result, comp_id, comp_title, username = query_tuple
    return PersonalBestRecord(
        personal_best = result,
        user_id       = user_id,
        username      = username,
        comp_id       = comp_id,
        comp_title    = comp_title
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


def _sort_by_speed(personal_bests):
    """ Sorts a list of PersonalBestRecords by `personal_best` which is either the single or
    average time/result. Takes into account DNFs, etc. """

    def _sort_pbs(pb_1, pb_2):
        """ Compares `personal_best` values from two PersonalBestRecords. Lack of a result
        to be sorted to the end, DNFs right before that, then compare time values directly. """
        val1 = pb_1.personal_best
        val2 = pb_2.personal_best
        if not val1:
            val1 = 100000000
        if not val2:
            val2 = 100000000
        if val1 == 'DNF':
            val1 = 99999999
        if val2 == 'DNF':
            val2 = 99999999
        return int(val1) - int(val2)

    def _cmp_to_key(mycmp):
        """ Converts a cmp= function into a key= function.
        Utility func for sorting custom objects by specified values. """
        # pylint: disable=C0103,C0111,W0613
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

    personal_bests.sort(key=_cmp_to_key(_sort_pbs))
    return personal_bests


def _determine_ranks(personal_bests):
    """ Takes an ordered list of PersonalBestRecords and assigns each PersonalBestRecord a rank.
    Ranks are the same for PersonalBestRecords with identical times.
    Ex: [12, 13, 14, 14, 15] would have ranks [1, 2, 3, 3, 5] """

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
    for i, personal_best in enumerate(personal_bests):
        personal_best.rank = ranked_times[i][0]

    return personal_bests


def get_ordered_pb_singles_for_event(event_id):
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
        group_by(UserEventResults.id, UserEventResults.user_id, UserEventResults.single, Competition.id, Competition.title, User.username).\
        order_by(UserEventResults.id.desc()).\
        values(UserEventResults.user_id, UserEventResults.single, Competition.id, Competition.title, User.username)
    # pylint: enable=C0301

    # NOTE: if adding anything to this tuple being selected in values(...) above, add it to the
    # end so that code indexing this tuple doesn't get all jacked. Make sure to make an identical
    # addition to `get_ordered_pb_averages_for_event` and update `_build_PersonalBestRecord`

    personal_bests = [_build_PersonalBestRecord(result) for result in results]
    personal_bests = _filter_one_pb_per_user(personal_bests)
    personal_bests = _sort_by_speed(personal_bests)
    personal_bests = _determine_ranks(personal_bests)

    return personal_bests


def get_ordered_pb_averages_for_event(event_id):
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
        group_by(UserEventResults.id, UserEventResults.user_id, UserEventResults.average, Competition.id, Competition.title, User.username).\
        order_by(UserEventResults.id.desc()).\
        values(UserEventResults.user_id, UserEventResults.average, Competition.id, Competition.title, User.username)
    # pylint: enable=C0301

    # NOTE: if adding anything to this tuple being selected in values(...) above, add it to the
    # end so that code indexing this tuple doesn't get all jacked. Make sure to make an identical
    # addition to `get_ordered_pb_singles_for_event` and update `_build_PersonalBestRecord`

    personal_bests = [_build_PersonalBestRecord(result) for result in results]

    # Some events don't have averages, so it's ok to just return an empty list. Checking here
    # instead of checking `results` above, because `results` is a generator and the contents have't
    # been iterated yet
    if not personal_bests:
        return list()

    personal_bests = _filter_one_pb_per_user(personal_bests)
    personal_bests = _sort_by_speed(personal_bests)
    personal_bests = _determine_ranks(personal_bests)

    return personal_bests
