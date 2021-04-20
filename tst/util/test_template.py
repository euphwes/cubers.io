from datetime import datetime
from urllib.parse import urlencode

import pytest

from cubersio.util.template import link_to_algcubingnet, slugify_filter, format_datetime, friendly_time, \
    format_fmc_result, format_mbld_result

# Extract the actual wrapped function from the Jinja context processor
from tst.util.events.test_mbld import __build_coded_result

link_to_algcubingnet_fn = link_to_algcubingnet()["link_to_algcubingnet"]


@pytest.mark.parametrize('setup, alg, moves_count', [
    ("U2 D2", "", 24),
    ("U2 D2", None, 24),
    ("", None, 24),
    (None, None, 24),
])
def test_link_to_algcubingnet_no_solution(setup, alg, moves_count):
    """ Test that the alg.cubing.net link context processor doesn't return a link in no solution/algorithm is provided,
    it just returns the move count as a string. """

    assert link_to_algcubingnet_fn(setup, alg, moves_count) == str(moves_count)


def test_link_to_algcubingnet():
    """ Tests that the alg.cubing.net link context processor returns a link with the expected values. """

    setup = "U2 D' F2 R"
    alg = "R2 L B2 D F R U2"
    moves_count = 7

    link = link_to_algcubingnet_fn(setup, alg, moves_count)

    expected_querystring = urlencode([
        ('setup', setup),
        ('alg', alg),
        ('type', 'reconstruction'),
    ])

    assert '<a href="https://alg.cubing.net/?' in link
    assert expected_querystring in link

    anchor_close_bracket_ix = link.index('>')
    assert link[anchor_close_bracket_ix+1: anchor_close_bracket_ix+1+len(str(moves_count))] == str(moves_count)


@pytest.mark.parametrize('input_value, expected_slug', [
    ("HELLO", "hello"),
    ("3x3", "3x3"),
    ("I like turtles", "i-like-turtles"),
    ("Square-1", "square-1"),
    ("PLL Time Attack", "pll-time-attack")
])
def test_slugify(input_value, expected_slug):
    assert slugify_filter(input_value) == expected_slug


def test_format_datetime():
    assert format_datetime(datetime(2019, 12, 2)) == "Dec 2, 2019"


@pytest.mark.parametrize('input_value, expected_friendly_time', [
    (2345, "23.45"),
    ("2345", "23.45"),
    (12345, "2:03.45"),
    ("12345", "2:03.45"),
    (None, ""),
    ("DNF", "DNF")
])
def test_friendly_time(input_value, expected_friendly_time):
    assert friendly_time(input_value) == expected_friendly_time


@pytest.mark.parametrize('input_value, expected_formatted_result', [
    (None, ''),
    ('DNF', 'DNF'),
    (2400, 24),
    (2400.00, 24),
    ("2400", 24)
])
def test_format_fmc_result(input_value, expected_formatted_result):
    assert format_fmc_result(input_value) == expected_formatted_result


@pytest.mark.parametrize('input_value, expected_formatted_result', [
    (None, ''),
    ('', ''),
    (0, ''),
    (__build_coded_result(20, 20, 145), '20/20 2:25'),
    (__build_coded_result(21, 22, 967), '21/22 16:07'),
])
def test_format_mbld_result(input_value, expected_formatted_result):
    assert format_mbld_result(input_value) == expected_formatted_result
