""" Tests for internal scramblers and scramble-related utility functions. """

import pytest

from app.util.events.scramblers.internal import mbld_scrambler, attack_scrambler, redi_scrambler, fmc_scrambler,\
    fifteen_puzzle_scrambler, scrambler_234_relay, scrambler_333_relay, does_fmc_scramble_have_cancellations


_222_SCRAMBLE = "U R2 U R' F2 U R' F2 U'"
_333_SCRAMBLE = "L2 D2 B2 L2 B2 U R2 U' F2 L2 U F' R' D2 B' L F D2 U L D"
_444_SCRAMBLE = "D R U L B L B U' F B2 L2 F2 L2 U2 L2 B' L2 U2 F U2 Fw2 D' R2 Uw2 Rw2 B' U2 F' R2 D' Rw2 L2 U' R' Uw2"


@pytest.mark.parametrize('scramble_fn', [
    mbld_scrambler,
    attack_scrambler,
    redi_scrambler,
    fifteen_puzzle_scrambler,
    fmc_scrambler,
    scrambler_234_relay,
    scrambler_333_relay
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


def test_333_relay_of_3(mocker):
    """ Tests that the 3x3 relay of 3 invokes scrambler333.get_WCA_scramble() and uses the returned values as the
    components of the combined scramble. """

    mocked_scrambler333 = mocker.patch('app.util.events.scramblers.internal.scrambler333')
    mocked_scrambler333.get_WCA_scramble.return_value = _333_SCRAMBLE

    for scramble_part in scrambler_333_relay().split('\n'):
        assert _333_SCRAMBLE in scramble_part

    assert mocked_scrambler333.get_WCA_scramble.call_count == 3


def test_234_relay_of_3(mocker):
    """ Tests that the 2-3-4 relay invokes the 2x2, 3x3, and 4x4 scramblers and uses those as the components of the
     combined scramble. """

    mocked_scrambler222 = mocker.patch('app.util.events.scramblers.internal.scrambler222')
    mocked_scrambler222.get_WCA_scramble.return_value = _222_SCRAMBLE

    mocked_scrambler333 = mocker.patch('app.util.events.scramblers.internal.scrambler333')
    mocked_scrambler333.get_WCA_scramble.return_value = _333_SCRAMBLE

    mocked_scrambler444 = mocker.patch('app.util.events.scramblers.internal.scrambler444')
    mocked_scrambler444.get_random_state_scramble.return_value = _444_SCRAMBLE

    scramble_parts = scrambler_234_relay().split('\n')
    assert _222_SCRAMBLE in scramble_parts[0]
    assert _333_SCRAMBLE in scramble_parts[1]
    assert _444_SCRAMBLE in scramble_parts[2]

    mocked_scrambler222.get_WCA_scramble.assert_called_once()
    mocked_scrambler333.get_WCA_scramble.assert_called_once()
    mocked_scrambler444.get_random_state_scramble.assert_called_once()


@pytest.mark.parametrize('num_faces', [1, 10])
def test_redi_scrambler_rotations(num_faces):
    """ Tests that the Redi Cube scrambler produces scrambles with the expected number of rotations. """

    assert len(redi_scrambler(num_faces).split(' x ')) == num_faces


def test_fmc_scrambler_calls_wca_333_scrambler(mocker):
    """ Tests that the FMC scrambler defers to the 3x3 WCA scrambler. """

    mocked_scrambler333 = mocker.patch('app.util.events.scramblers.internal.scrambler333')
    mocked_scrambler333.get_WCA_scramble.return_value = _333_SCRAMBLE

    assert _333_SCRAMBLE in fmc_scrambler()

    mocked_scrambler333.get_WCA_scramble.assert_called_once()


def test_fmc_scrambler_pads_wca_scramble(mocker):
    """ Tests that the FMC scrambler correctly pads the WCA scramble with R' U' F. """

    mocked_scrambler333 = mocker.patch('app.util.events.scramblers.internal.scrambler333')
    mocked_scrambler333.get_WCA_scramble.return_value = _333_SCRAMBLE

    scramble = fmc_scrambler()

    assert scramble.startswith("R' U' F")
    assert scramble.endswith("R' U' F")


def test_does_fmc_scramble_have_cancellations_no_cancellations():
    """ Tests that the function returns false if the provided scramble does not have a cancellation with the standard
    WCA FMC scramble padding. """

    assert not does_fmc_scramble_have_cancellations(_333_SCRAMBLE)


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
