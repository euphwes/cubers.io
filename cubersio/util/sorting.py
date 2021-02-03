""" Utilities for sorting collections of various types of objects. """

from cubersio.persistence.models import EventFormat

from ranking import Ranking

# -------------------------------------------------------------------------------------------------

def cmp_to_key(mycmp):
    """ Converts a cmp= function into a key= function. This facilitates writing comparator functions
    for custom sorting of objects based on their attributes. """

    class Comparator:
        """ A wrapper around the custom comparator function which turns it into a Comparator object,
        which is suitable as the `key` argument for Python's `sort` from the stdlib. """

        def __init__(self, obj):
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

    return Comparator


def cmp_to_key_wrapped(func):
    """ A decorator for cleanly wrapping a comparator function in `cmp_to_key`. """

    return cmp_to_key(func)

# -------------------------------------------------------------------------------------------------

@cmp_to_key_wrapped
def sort_personal_best_records(pb1, pb2):
    """ Compares two PersonalBestRecords based on their `personal_best` field. Lack of a result
    to be sorted to the end, DNFs right before that, then compare time values directly. """

    val1 = pb1.personal_best
    val2 = pb2.personal_best
    if not val1:
        val1 = 100000000
    if not val2:
        val2 = 100000000
    if val1 == 'DNF':
        val1 = 99999999
    if val2 == 'DNF':
        val2 = 99999999
    return int(val1) - int(val2)


def sort_user_results_with_rankings(results, event_format):
    """ Sorts a list of UserEventResults based on the event format (for tie-breaking), and then
    applies rankings (identical results receive identical rankings). Returns a list of tuples of
    the form (ranking, visible_ranking, userEventResult), where ranking is the raw numerical
    rank and visible_ranking is the same as ranking except duplicate ranks show as an empty string. """

    ranked_results = list()

    # Best-of-N results are only ranked by singles
    if event_format in [EventFormat.Bo1, EventFormat.Bo3]:
        results.sort(key=__sort_user_event_results_by_result)

        # Build a list of just the time singles to be fed into the ranking mechanism.
        # If the time value cannot be interpreted as an int, it's probably a DNF so just pretend
        # it's some humongous value which would sorted at the end
        times_values = list()
        for result in results:
            try:
                times_values.append(int(result.result))
            except ValueError:
                times_values.append(9999999999999)

        # Rank the list of times
        ranked_times = list(Ranking(times_values, start=1, reverse=True))
        ranks_seen = set()
        for i, r in enumerate(ranked_times):
            rank = r[0]
            visible_rank = rank
            if rank not in ranks_seen:
                ranks_seen.add(rank)
            else:
                visible_rank = ''
            ranked_results.append((rank, visible_rank, results[i]))

    else:
        # Sort by single first, to ensure any ties by overall result (average/mean) are broken by
        # the singles
        results.sort(key=__sort_user_event_results_by_single)
        results.sort(key=__sort_user_event_results_by_result)

        # Build a list of tuples (average/mean, single), to be fed into the ranking mechanism
        # If the time value cannot be interpreted as an int, it's probably a DNF so just pretend
        # it's some humongous value which would sorted at the end
        times_values = list()
        for result in results:
            try:
                average = int(result.result)
            except ValueError:
                average = 9999999999999
            try:
                single = int(result.single)
            except ValueError:
                single = 9999999999999
            times_values.append((average, single))

        # Rank the list of times tuples
        ranked_times = list(Ranking(times_values, start=1, reverse=True))
        ranks_seen = set()
        for i, r in enumerate(ranked_times):
            rank = r[0]
            visible_rank = rank
            if rank not in ranks_seen:
                ranks_seen.add(rank)
            else:
                visible_rank = ''
            ranked_results.append((rank, visible_rank, results[i]))

    return ranked_results


@cmp_to_key_wrapped
def __sort_user_event_results_by_result(val1, val2):
    """ Compares two UserEventResults based on their `result` field. Lack of a result
    to be sorted to the end, DNFs right before that, then compare time values directly. """

    result1 = val1.result
    result2 = val2.result
    if not result1:
        result1 = 100000000
    if not result2:
        result2 = 100000000
    if result1 == 'DNF':
        result1 = 99999999
    if result2 == 'DNF':
        result2 = 99999999
    return int(result1) - int(result2)


@cmp_to_key_wrapped
def __sort_user_event_results_by_single(val1, val2):
    """ Compares two UserEventResults based on their `single` field. Lack of a single
    to be sorted to the end, DNFs right before that, then compare time values directly. """

    single1 = val1.single
    single2 = val2.single if val2 else 100000000
    if not single1:
        single1 = 100000000
    if not single2:
        single2 = 100000000
    if single1 == 'DNF':
        single1 = 99999999
    if single2 == 'DNF':
        single2 = 99999999
    return int(single1) - int(single2)
