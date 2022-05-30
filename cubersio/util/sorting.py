""" Utilities for sorting collections of various types of objects. """

from functools import cmp_to_key
from typing import List, Tuple

from ranking import Ranking

from cubersio.persistence.models import EventFormat, PersonalBestRecord, UserEventResults


@cmp_to_key
def sort_personal_best_records(pb1: PersonalBestRecord, pb2: PersonalBestRecord) -> int:
    """ Compares two PersonalBestRecords based on their `personal_best` field. Lack of a result to be sorted to the end,
    DNFs right before that, then compare time values directly. """

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


@cmp_to_key
def __sort_user_event_results_by_result(result1: UserEventResults, result2: UserEventResults) -> int:
    """ Compares two UserEventResults based on their `result` field. Lack of a result to be sorted to the end,
    DNFs right before that, then compare time values directly. """

    val1 = result1.result
    val2 = result2.result
    if not val1:
        val1 = 100000000
    if not val2:
        val2 = 100000000
    if val1 == 'DNF':
        val1 = 99999999
    if val2 == 'DNF':
        val2 = 99999999
    return int(val1) - int(val2)


@cmp_to_key
def __sort_user_event_results_by_single(result1: UserEventResults, result2: UserEventResults) -> int:
    """ Compares two UserEventResults based on their `single` field. Lack of a single to be sorted to the end,
    DNFs right before that, then compare time values directly. """

    val1 = result1.single
    val2 = result2.single if result2 else 100000000
    if not val1:
        val1 = 100000000
    if not val2:
        val2 = 100000000
    if val1 == 'DNF':
        val1 = 99999999
    if val2 == 'DNF':
        val2 = 99999999
    return int(val1) - int(val2)


def sort_user_results_with_rankings(results: List[UserEventResults],
                                    event_format: EventFormat) -> List[Tuple[int, str, UserEventResults]]:
    """ Sorts a list of UserEventResults based on the event format (for tie-breaking), and then applies rankings
    (identical results receive identical rankings). Returns a list of tuples of the form (ranking, visible_ranking,
    userEventResult), where ranking is the raw numerical rank and visible_ranking is the same as ranking except
    duplicate ranks show as an empty string. """

    # Best-of-N results are only ranked by singles
    if event_format in [EventFormat.Bo1, EventFormat.Bo3]:
        results.sort(key=__sort_user_event_results_by_result)

    # Average/mean results are sorted by single first, to ensure any ties by overall result (average/mean) are broken
    # by the singles.
    else:
        results.sort(key=__sort_user_event_results_by_single)
        results.sort(key=__sort_user_event_results_by_result)

    # Build a list of tuples (average/mean, single), to be fed into the ranking mechanism.
    # If the time value cannot be interpreted as an int, it's a "DNF" or None, so just assign it some humongous value
    # which would sorted at the end.
    times_values = list()
    for result in results:
        try:
            average = int(result.result)
        except (ValueError, TypeError):
            average = 9999999999999
        try:
            single = int(result.single)
        except (ValueError, TypeError):
            single = 9999999999999
        times_values.append((average, single))

    # Ensure sort is valid after building the tuples with DNF/None reprs, and sort again.
    if event_format in [EventFormat.Bo1, EventFormat.Bo3]:
        times_values.sort(key=lambda x: x[1])
    else:
        times_values.sort(key=lambda x: x[1])
        times_values.sort(key=lambda x: x[0])

    # Rank the list of times tuples. Legitimately tied results will have the same rank, so we also send back a
    # "visible rank" which facilitates showing the results nicely. Ranks with ties will look something like this:
    #
    #   Place     Result
    #   -----     ------
    #     1        10.2
    #     2        15
    #              15
    #     4        17.84

    ranks_seen = set()
    ranked_results = list()

    for i, r in enumerate(Ranking(times_values, start=1, reverse=True)):
        rank = r[0]
        if rank not in ranks_seen:
            ranks_seen.add(rank)
            visible_rank = str(rank)
        else:
            visible_rank = ''
        ranked_results.append((rank, visible_rank, results[i]))

    return ranked_results
