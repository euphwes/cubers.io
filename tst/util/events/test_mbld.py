""" Tests for the MbldSolve class. """

import pytest
from math import isclose

from cubersio.util.events.mbld import MbldSolve


def __build_coded_result(successful, attempted, time_seconds):
    # The format of a coded solve is XXYYYYZZ
    #   XX   = (99 - number of points)
    #   YYYY = elapsed seconds (4 digits, padded with insignificant zeros)
    #   ZZ   = number missed (2 digits, padded with insignificant zeros)
    points = 2*successful - attempted
    seconds = str(int(time_seconds)).zfill(4)
    missed = str(attempted - successful).zfill(2)
    result = str(99 - points) + seconds + missed

    # Trim off leading zeros, to make sure that we exercise the zero-padding logic in MbldSolve
    while result.startswith('0'):
        result = result[1:]

    return result


@pytest.mark.parametrize('coded_value, expected_attempted', [
    (__build_coded_result(1, 1, 456), 1),
    (__build_coded_result(8, 10, 456), 10),
    (__build_coded_result(15, 25, 456), 25),
    (__build_coded_result(95, 95, 3500), 95)
])
def test_mbld_solve_parses_correct_attempted(coded_value, expected_attempted):
    """ Test that MbldSolve properly parses the number of attempted cubes from a coded MBLD solve value, for MBLD
    attempts which are not DNFs. """

    assert MbldSolve(coded_value).attempted == expected_attempted


@pytest.mark.parametrize('coded_value, expected_successful', [
    (__build_coded_result(1, 1, 456), 1),
    (__build_coded_result(10, 10, 456), 10),
    (__build_coded_result(15, 25, 456), 15)
])
def test_mbld_solve_parses_correct_successful(coded_value, expected_successful):
    """ Test that MbldSolve properly parses the number of successful cubes from a coded MBLD solve value, for MBLD
    attempts which are not DNFs. """

    assert MbldSolve(coded_value).successful == expected_successful


@pytest.mark.parametrize('coded_value, expected_points', [
    (__build_coded_result(1, 1, 456), 1),
    (__build_coded_result(2, 2, 456), 2),
    (__build_coded_result(8, 10, 456), 6),
    (__build_coded_result(15, 25, 456), 5)
])
def test_mbld_solve_calculates_correct_points(coded_value, expected_points):
    """ Test that MbldSolve properly calculates the number of points from a coded MBLD solve value, for MBLD attempts
    which are not DNFs. """

    assert MbldSolve(coded_value).points == expected_points


@pytest.mark.parametrize('coded_value, expected_fractional_hour_remaining', [
    (__build_coded_result(1, 1, 30), 0.99167),
    (__build_coded_result(1, 1, 15 * 60), 0.75),
    (__build_coded_result(1, 1, 42 * 60), 0.30),
    (__build_coded_result(1, 1, 57.5 * 60), 0.04167),
    (__build_coded_result(1, 1, 60 * 60), 0),
])
def test_mbld_solve_calculates_correct_points(coded_value, expected_fractional_hour_remaining):
    """ Test that MbldSolve calculates the correct fractional hour remaining from a coded MBLD solve value, for MBLD
    attempts which are not DNFs. """

    assert isclose(MbldSolve(coded_value).fractional_hour_remaining, expected_fractional_hour_remaining, rel_tol=1e-3)


def test_mbld_solve_str(mocker):
    """ Tests that MbldSolve builds the expected str representation, and calls to the time conversion utility with the
    expected parameter. """

    module = 'cubersio.util.events.mbld'
    mocked_convert_centis = mocker.patch(module + '.convert_centiseconds_to_friendly_time', return_value="2:03.00")

    assert str(MbldSolve(__build_coded_result(2, 3, 123))) == '2/3 2:03'
    mocked_convert_centis.assert_called_once_with(12300)


def test_mbld_dnf():
    """ Tests that a DNF result returns DNF. """

    assert str(MbldSolve('DNF')) == 'DNF'


def test_mbld_dnf_has_points_and_sort_value():
    """ Tests that a DNF result has a points value and sort value. """

    dnf_mbld = MbldSolve('DNF')
    assert dnf_mbld.points == 0
    assert dnf_mbld.sort_value == 0