""" Tests for internal scramblers and scramble-related utility functions. """

import pytest

from cubersio.util.events.scramblers.internal import mbld_scrambler, attack_scrambler, redi_scrambler, fmc_scrambler,\
    fifteen_puzzle_scrambler, scrambler_234_relay, scrambler_333_relay, does_fmc_scramble_have_cancellations,\
    scrambler222, scrambler333, scrambler444


_222_SCRAMBLE = "U R2 U R' F2 U R' F2 U'"
_333_SCRAMBLE = "L2 D2 B2 L2 B2 U L F D2 U L D"
_444_SCRAMBLE = "D R U L B L B U' F B2 L2 F2 L2 U2 L2 B' L2 U2 F U2 Fw2 D' R2 Uw2 Rw2 B' U2 F' R2 D' Rw2 L2 U' R' Uw2"


@pytest.fixture
def mock_cube_scramblers(mocker):
    mocker.patch('cubersio.util.events.scramblers.internal.scrambler222.get_WCA_scramble', return_value=_222_SCRAMBLE)
    mocker.patch('cubersio.util.events.scramblers.internal.scrambler333.get_WCA_scramble', return_value=_333_SCRAMBLE)
    mocker.patch('cubersio.util.events.scramblers.internal.scrambler444.get_random_state_scramble',
                 return_value=_444_SCRAMBLE)


@pytest.mark.parametrize('scramble_fn', [
    mbld_scrambler,
    attack_scrambler,
    redi_scrambler,
    fifteen_puzzle_scrambler,
    fmc_scrambler,
    scrambler_234_relay,
    scrambler_333_relay,
])
def test_internal_scramblers_return_string(scramble_fn):
    """ Tests that the basic scramblers return strings as expected. """

    assert isinstance(scramble_fn(), str)


@pytest.mark.parametrize('relay_fn, num_parts', [
    (scrambler_333_relay, 3),
    (scrambler_234_relay, 3)
])
def test_relays_have_correct_numbers_of_parts(relay_fn, num_parts):
    """ Tests that the relay scrambler functions return the correct number of parts. """

    assert len(relay_fn().split('\n')) == num_parts


@pytest.mark.usefixtures('mock_cube_scramblers')
def test_333_relay_of_3():
    """ Tests that the 3x3 relay of 3 invokes scrambler333.get_WCA_scramble() and uses the returned values as the
    components of the combined scramble. """

    for scramble_part in scrambler_333_relay().split('\n'):
        assert _333_SCRAMBLE in scramble_part

    assert scrambler333.get_WCA_scramble.call_count == 3


@pytest.mark.usefixtures('mock_cube_scramblers')
def test_234_relay_of_3():
    """ Tests that the 2-3-4 relay invokes the 2x2, 3x3, and 4x4 scramblers and uses those as the components of the
     combined scramble. """

    scramble_parts = scrambler_234_relay().split('\n')

    assert _222_SCRAMBLE in scramble_parts[0]
    assert _333_SCRAMBLE in scramble_parts[1]
    assert _444_SCRAMBLE in scramble_parts[2]

    scrambler222.get_WCA_scramble.assert_called_once()
    scrambler333.get_WCA_scramble.assert_called_once()
    scrambler444.get_random_state_scramble.assert_called_once()


@pytest.mark.parametrize('num_faces', [1, 10])
def test_redi_scrambler_rotations(num_faces):
    """ Tests that the Redi Cube scrambler produces scrambles with the expected number of rotations. """

    assert len(redi_scrambler(num_faces).split(' x ')) == num_faces


@pytest.mark.usefixtures('mock_cube_scramblers')
def test_fmc_scrambler_calls_wca_333_scrambler():
    """ Tests that the FMC scrambler defers to the 3x3 WCA scrambler. """

    assert _333_SCRAMBLE in fmc_scrambler()
    scrambler333.get_WCA_scramble.assert_called_once()


@pytest.mark.usefixtures('mock_cube_scramblers')
def test_fmc_scrambler_pads_wca_scramble():
    """ Tests that the FMC scrambler correctly pads the WCA scramble with R' U' F. """

    scramble = fmc_scrambler()

    assert scramble.startswith("R' U' F")
    assert scramble.endswith("R' U' F")


@pytest.mark.parametrize('scramble, expected_result', [
    ("F2 rest of scramble does not matter", True),
    ("rest of scramble does not matter R", True),
    ("B F' rest of scramble does not matter", True),
    ("rest of scramble does not matter R2 L", True),
    (_333_SCRAMBLE, False)
])
def test_does_fmc_scramble_have_cancellations(scramble, expected_result):
    """ Tests that the function returns the expected result about whether the provided scramble has cancellations with
    the standard FMC padding. """

    assert does_fmc_scramble_have_cancellations(scramble) == expected_result


def test_fmc_scramblers_runs_until_no_cancellations(mocker):

    module = "cubersio.util.events.scramblers.internal."
    mocked_has_cancellations = mocker.patch(module + 'does_fmc_scramble_have_cancellations', side_effect=[True, False])

    fmc_scrambler()
    assert mocked_has_cancellations.call_count == 2


@pytest.fixture
def mock_15_scramblers(mocker):
    mocked_random_moves = mocker.patch('cubersio.util.events.scramblers.internal.get_random_moves_scramble')
    mocked_random_state = mocker.patch('cubersio.util.events.scramblers.internal.get_random_state_scramble')
    return mocked_random_moves, mocked_random_state


@pytest.mark.usefixtures('mock_15_scramblers')
@pytest.mark.parametrize('is_devo, random_state_calls, random_moves_calls', [
    (True, 0, 1),
    (False, 1, 0),
])
def test_fifteen_puzzle_scrambler_calls_correct_impl(is_devo, random_state_calls, random_moves_calls,
                                                     mock_15_scramblers, mocker):
    """ Tests that the 15 Puzzle scrambler uses a random-moves implementation in devo, and uses a random-state
    implementation in prod. Also tests that the scramblers are called with a value of '4' indicating a 4x4 grid, aka
    a 15 Puzzle and not an 8 Puzzle (n=3), etc. """

    mocked_random_moves, mocked_random_state = mock_15_scramblers
    mocker.patch.dict("cubersio.util.events.scramblers.internal.app.config", {'IS_DEVO': is_devo})

    fifteen_puzzle_scrambler()

    assert mocked_random_moves.call_count == random_moves_calls
    assert mocked_random_state.call_count == random_state_calls

    if is_devo:
        mocked_random_moves.assert_called_with(4)
    else:
        mocked_random_state.assert_called_with(4)
