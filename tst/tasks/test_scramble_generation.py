""" Tests for scramble generation background tasks. """

from unittest.mock import Mock, patch, call

import pytest
from huey.exceptions import TaskException

from cubersio.tasks import huey
from cubersio.tasks.scramble_generation import check_scramble_pool, ScramblePoolTopOffInfo, top_off_scramble_pool
from cubersio.util.events.resources import EVENT_3x3, EVENT_10x10, EVENT_COLL, EVENT_FTO, EVENT_REX

# Put Huey in immediate mode so the tasks execute synchronously
huey.immediate = True


def _setup_mock(**kwargs):
    """ Utility function for setting up a mocked Event or EventDefinition. Need to use Mock::configure because Events
    and EventDefinitions have a `name` attribute which we need to override, and `name` is usually a special reserved
    attribute for Mock. """

    mock_event = Mock()
    mock_event.configure_mock(**kwargs)

    return mock_event


@patch('cubersio.tasks.scramble_generation.get_all_events')
@patch('cubersio.tasks.scramble_generation.top_off_scramble_pool')
def test_check_scramble_pool(mock_top_off_scramble_pool, mock_get_all_events):
    """ Test that the scrambler pool checker task makes the appropriate calls to top_off_scramble_pool based on the
    number of remaining scrambles for each event. """

    # 3x3 and FTO need scrambles, they are below the 2x weekly scrambles threshold.
    # 10x10 has enough scrambles, and COLL doesn't have its scrambles pre-generated.
    mock_get_all_events.return_value = [
        _setup_mock(name=EVENT_3x3.name, id=1, scramble_pool=list(range(5)), totalSolves=5),
        _setup_mock(name=EVENT_10x10.name, id=2, scramble_pool=list(range(5)), totalSolves=1),
        _setup_mock(name=EVENT_COLL.name, id=3, scramble_pool=list(range(5)), totalSolves=5),
        _setup_mock(name=EVENT_FTO.name, id=4, scramble_pool=list(), totalSolves=5),
    ]

    check_scramble_pool()

    mock_get_all_events.assert_called_once()
    assert mock_top_off_scramble_pool.call_count == 2
    mock_top_off_scramble_pool.assert_has_calls([
        call(ScramblePoolTopOffInfo(1, EVENT_3x3.name, 5)),
        call(ScramblePoolTopOffInfo(4, EVENT_FTO.name, 10))
    ])


@pytest.mark.parametrize('top_off_info', [
    ScramblePoolTopOffInfo(event_id=10, event_name=EVENT_REX.name, num_scrambles=5),
    ScramblePoolTopOffInfo(event_id=42, event_name=EVENT_FTO.name, num_scrambles=15),
])
@patch('cubersio.tasks.scramble_generation.add_scramble_to_scramble_pool')
@patch('cubersio.tasks.scramble_generation.get_event_definition_for_name')
def test_top_off_scramble_pool_multi_scramble_puzzles(mock_get_event_definition_for_name,
                                                      mock_add_scramble_to_scramble_pool,
                                                      top_off_info: ScramblePoolTopOffInfo):
    """ Test that top_off_scramble_pool calls the event resource scrambler correctly for those events where scrambles
    are generated in bulk because it's faster. """

    scrambles = list(range(top_off_info.num_scrambles))
    mock_event_def = _setup_mock(name=top_off_info.event_name)
    mock_event_def.get_multiple_scrambles.return_value = scrambles

    mock_get_event_definition_for_name.return_value = mock_event_def

    top_off_scramble_pool(top_off_info)

    mock_get_event_definition_for_name.assert_called_once_with(top_off_info.event_name)
    mock_event_def.get_multiple_scrambles.assert_called_once_with(top_off_info.num_scrambles)

    assert mock_add_scramble_to_scramble_pool.call_count == top_off_info.num_scrambles

    expected_calls = [call(scramble, top_off_info.event_id) for scramble in scrambles]
    mock_add_scramble_to_scramble_pool.assert_has_calls(expected_calls)


@patch('cubersio.tasks.scramble_generation.add_scramble_to_scramble_pool')
@patch('cubersio.tasks.scramble_generation.get_event_definition_for_name')
def test_top_off_scramble_pool_single_scramble_puzzles(mock_get_event_definition_for_name,
                                                       mock_add_scramble_to_scramble_pool):
    """ Test that top_off_scramble_pool calls the event resource scrambler correctly for those events where scrambles
    are generated one at a time. """

    top_off_info = ScramblePoolTopOffInfo(event_id=11, event_name=EVENT_3x3.name, num_scrambles=5)

    scrambles = list(range(top_off_info.num_scrambles))
    mock_event_def = _setup_mock(name=top_off_info.event_name)
    mock_event_def.get_scramble.side_effect = scrambles

    mock_get_event_definition_for_name.return_value = mock_event_def

    top_off_scramble_pool(top_off_info)

    mock_get_event_definition_for_name.assert_called_once_with(top_off_info.event_name)

    assert mock_event_def.get_scramble.call_count == top_off_info.num_scrambles
    assert mock_add_scramble_to_scramble_pool.call_count == top_off_info.num_scrambles

    expected_calls = [call(scramble, top_off_info.event_id) for scramble in scrambles]
    mock_add_scramble_to_scramble_pool.assert_has_calls(expected_calls)


@patch('cubersio.tasks.scramble_generation.get_event_definition_for_name')
def test_top_off_scramble_pool_raises_for_nonexistent_event(mock_get_event_definition_for_name):
    """ Test that top_off_scramble_pool raises RuntimeError for a bogus event. """

    mock_get_event_definition_for_name.return_value = None
    with pytest.raises(TaskException) as te:
        top_off_scramble_pool(ScramblePoolTopOffInfo(event_id=1, event_name="blah", num_scrambles=5)).get()
    assert f"Can't find an EventResource for event blah" in te.value.metadata['error']
