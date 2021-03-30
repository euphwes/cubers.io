""" Tests for sliding tile scramblers and utility functions. """

import pytest
import random

from cubersio.util.events.scramblers.sliding_tile import get_random_moves_scramble, get_random_state_scramble


@pytest.mark.parametrize('scramble_fn', [
    get_random_moves_scramble,
    get_random_state_scramble,
])
def test_sliding_tile_scramblers_return_string(scramble_fn):
    """ Tests that the scramblers return strings as expected. Use n=3 (8 Puzzle) rather than n=4+, because the random
    state scrambles for those take a long time to build. """

    assert isinstance(scramble_fn(3), str)


@pytest.mark.parametrize('num_moves', [1, 10, 100])
def test_get_random_moves_scramble_returns_correct_number_of_moves(num_moves):
    """ Tests that the random moves scrambler returns the correct number of moves. """

    # Can't just count each piece, because something like 'U U' would be reduced to 'U2' and that needs to be counted
    # as 2 moves.
    count = 0
    for move in get_random_moves_scramble(4, num_moves).split(' '):
        count += 1 if len(move) == 1 else int(move[-1])

    assert count == num_moves


def test_get_random_state_scramble_success(mocker):
    """ Tests the random state scrambler happy path and makes sure it calls the expected dependencies. """

    n = 3
    seed = 113
    expected_solved_state = list(range(1, n**2)) + [0]
    expected_shuffled_state = [0, 4, 8, 3, 7, 2, 6, 1, 5]
    steps_to_solved = ['content', 'here', 'doesnt', 'matter', 'for', 'mocks']
    expected_scramble = 'U2 D L R'

    module = 'cubersio.util.events.scramblers.sliding_tile.'
    mock_is_solvable = mocker.patch(module + '__is_solvable', return_value=True)
    mock_ida_star_search = mocker.patch(module + '__ida_star_search', return_value=steps_to_solved)
    mock_convert_steps = mocker.patch(module + '__convert_steps_to_scramble', return_value=expected_scramble)

    random.seed(seed)
    returned_scramble = get_random_state_scramble(n)

    mock_is_solvable.assert_called_once_with(expected_shuffled_state, expected_solved_state, n)
    mock_ida_star_search.assert_called_once_with(tuple(expected_shuffled_state), tuple(expected_solved_state), n)
    mock_convert_steps.assert_called_once_with(steps_to_solved)
    assert returned_scramble == expected_scramble


def test_get_random_state_scramble_reshuffles_if_unsolvable(mocker):
    """ Tests that the random state scrambler re-shuffles the puzzle if a random state is not solvable. """

    n = 3
    seed = 113
    expected_solved_state = list(range(1, n**2)) + [0]
    shuffled_state_1 = [0, 4, 8, 3, 7, 2, 6, 1, 5]
    shuffled_state_2 = [4, 7, 5, 1, 8, 3, 6, 2, 0]
    expected_call_args = [
        (shuffled_state_1, expected_solved_state, n),
        (shuffled_state_2, expected_solved_state, n),
    ]

    def side_effect(shuffled_state, _, __):
        if shuffled_state == shuffled_state_1:
            return False
        if shuffled_state == shuffled_state_2:
            return True
        raise Exception("Shouldn't get here")

    module = 'cubersio.util.events.scramblers.sliding_tile.'
    mock_is_solvable = mocker.patch(module + '__is_solvable', side_effect=side_effect)

    random.seed(seed)
    get_random_state_scramble(n)

    assert mock_is_solvable.call_count == 2
    assert [args for args, kwargs in mock_is_solvable.call_args_list] == expected_call_args

