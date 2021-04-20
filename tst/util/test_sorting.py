""" Tests for custom sorting functions for sorting cubers.io domain objects. """

# TODO test docstrings

import pytest
from itertools import permutations

from cubersio.business.rankings import PersonalBestRecord
from cubersio.persistence.models import UserEventResults, EventFormat
from cubersio.util.sorting import sort_personal_best_records, __sort_user_event_results_by_result, \
    __sort_user_event_results_by_single, sort_user_results_with_rankings


_PB1 = PersonalBestRecord(personal_best=500)
_PB2 = PersonalBestRecord(personal_best=100)
_PB3 = PersonalBestRecord(personal_best=None)
_PB4 = PersonalBestRecord(personal_best="DNF")

_UNSORTED_PBS = [_PB1, _PB2, _PB3, _PB4]
_CORRECTLY_SORTED_PBS = [_PB2, _PB1, _PB4, _PB3]


@pytest.mark.parametrize('unsorted_pbs', permutations(_UNSORTED_PBS))
def test_sort_personal_best_records(unsorted_pbs):
    assert sorted(unsorted_pbs, key=sort_personal_best_records) == _CORRECTLY_SORTED_PBS


_RESULT1 = UserEventResults(result=500, single=500)
_RESULT2 = UserEventResults(result=100, single=100)
_RESULT3 = UserEventResults(result=None, single=None)
_RESULT4 = UserEventResults(result="DNF", single="DNF")

_UNSORTED_RESULTS = [_RESULT1, _RESULT2, _RESULT3, _RESULT4]
_CORRECTLY_SORTED_RESULTS = [_RESULT2, _RESULT1, _RESULT4, _RESULT3]


@pytest.mark.parametrize('unsorted_results', permutations(_UNSORTED_RESULTS))
def test_sort_user_event_results_by_result(unsorted_results):
    assert sorted(unsorted_results, key=__sort_user_event_results_by_result) == _CORRECTLY_SORTED_RESULTS


@pytest.mark.parametrize('unsorted_results', permutations(_UNSORTED_RESULTS))
def test_sort_user_event_results_by_single(unsorted_results):
    assert sorted(unsorted_results, key=__sort_user_event_results_by_single) == _CORRECTLY_SORTED_RESULTS


@pytest.mark.parametrize('event_format', [EventFormat.Bo1, EventFormat.Bo3])
def test_sort_user_results_with_rankings_best_of_format(event_format):
    r1 = UserEventResults(result=100)
    r2 = UserEventResults(result=1000)
    r3 = UserEventResults(result=1000)
    r4 = UserEventResults(result="DNF")
    results = [r1, r2, r3, r4]

    assert sort_user_results_with_rankings(results, event_format) == [
        (1, '1', r1),
        (2, '2', r2),
        (2, '', r3),
        (4, '4', r4),
    ]


@pytest.mark.parametrize('event_format', [EventFormat.Mo3, EventFormat.Ao5])
def test_sort_user_results_with_rankings_mean_average_formats(event_format):
    r1 = UserEventResults(result=100, single=100)
    r2 = UserEventResults(result=1000, single=1000)
    r3 = UserEventResults(result=1000, single=1000)
    r4 = UserEventResults(result=1000, single=800)
    r5 = UserEventResults(result="DNF", single=800)
    r6 = UserEventResults(result="DNF", single="DNF")
    results = [r1, r2, r3, r4, r5, r6]

    assert sort_user_results_with_rankings(results, event_format) == [
        (1, '1', r1),
        (2, '2', r4),
        (3, '3', r2),
        (3, '', r3),
        (5, '5', r5),
        (6, '6', r6),
    ]
