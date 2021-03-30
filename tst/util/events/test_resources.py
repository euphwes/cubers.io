""" Tests for the internal event definitions, and utility functions related to retrieving subsets of these events and
sorting event-related data. """

from unittest.mock import Mock

import pytest

from cubersio.util.events.resources import sort_comp_events_by_global_sort_order, sort_events_by_global_sort_order, \
    get_bonus_events_rotation_starting_at, get_bonus_events_without_current, get_event_definition_for_name, EVENT_3x3,\
    EVENT_4x4, EVENT_5x5, EVENT_FTO, EVENT_REDI, BONUS_EVENTS, EVENT_Mirror, EVENT_333Relay, EVENT_3x3_Feet
from cubersio.persistence.models import Event


def __build_mock_comp_event(name):
    mock_event = Mock()
    mock_event.Event.name = name
    return mock_event


__COMP_EVENT_333  = __build_mock_comp_event(EVENT_3x3.name)
__COMP_EVENT_444  = __build_mock_comp_event(EVENT_4x4.name)
__COMP_EVENT_555  = __build_mock_comp_event(EVENT_5x5.name)
__COMP_EVENT_FTO  = __build_mock_comp_event(EVENT_FTO.name)
__COMP_EVENT_REDI = __build_mock_comp_event(EVENT_REDI.name)

__EVENT_333  = Event(name=EVENT_3x3.name)
__EVENT_444  = Event(name=EVENT_4x4.name)
__EVENT_555  = Event(name=EVENT_5x5.name)
__EVENT_FTO  = Event(name=EVENT_FTO.name)
__EVENT_REDI = Event(name=EVENT_REDI.name)


def test_sort_comp_events_by_global_sort_order():
    """ Tests that sort_comp_events_by_global_sort_order correctly sorts CompetitionEvents by global sort order. """

    input_comp_events = [
        __COMP_EVENT_FTO,
        __COMP_EVENT_555,
        __COMP_EVENT_REDI,
        __COMP_EVENT_333
    ]

    expect_comp_events = [
        __COMP_EVENT_333,
        __COMP_EVENT_555,
        __COMP_EVENT_FTO,
        __COMP_EVENT_REDI,
    ]

    assert sort_comp_events_by_global_sort_order(input_comp_events) == expect_comp_events


def test_sort_events_by_global_sort_order():
    """ Tests that sort_events_by_global_sort_order correctly sorts Events by global sort order. """

    input_events = [
        __EVENT_FTO,
        __EVENT_555,
        __EVENT_REDI,
        __EVENT_333
    ]

    expected_events = [
        __EVENT_333,
        __EVENT_555,
        __EVENT_FTO,
        __EVENT_REDI,
    ]

    assert sort_events_by_global_sort_order(input_events) == expected_events


@pytest.mark.parametrize('starting_index', [0, 1, len(BONUS_EVENTS)-1])
def test_get_bonus_events_rotation_starting_at_correct_starting_index(starting_index):
    """ Tests that get_bonus_events_rotation_starting_at returns the bonus events starting at the correct index in the
    master bonus events list. """

    assert get_bonus_events_rotation_starting_at(starting_index, 1)[0] == BONUS_EVENTS[starting_index]


def test_get_bonus_events_rotation_starting_at_wraps_around():
    """ Tests that get_bonus_events_rotation_starting_at wraps around to the beginning of the list as expected, if the
    count is more than the number of items remaining in the list at the specified index. """

    events = get_bonus_events_rotation_starting_at(len(BONUS_EVENTS) - 1, 5)
    assert events[1] == BONUS_EVENTS[0]


def test_get_bonus_events_without_current():
    """ Tests that get_bonus_events_without_current returns only bonus events, and does not return the events which the
    caller doesn't want. """

    undesired_events = [BONUS_EVENTS[i] for i in (0, 4, 8, 11)]
    retrieved_events = get_bonus_events_without_current(undesired_events)

    assert all(event not in retrieved_events for event in undesired_events)
    assert all(event in BONUS_EVENTS for event in retrieved_events)


@pytest.mark.parametrize('event_name, expected_event_definition', [
    ("3x3", EVENT_3x3),
    ("FTO", EVENT_FTO),
    ("3x3 Mirror Blocks/Bump", EVENT_Mirror),
    ("3x3 Relay of 3", EVENT_333Relay),
    ("3x3 With Feet", EVENT_3x3_Feet),
    ("11x11 MBLD With Feet", None)
])
def test_get_event_definition_for_name(event_name, expected_event_definition):
    """ Tests that get_event_definition_for_name returns the expected event definition. """

    assert get_event_definition_for_name(event_name) == expected_event_definition
