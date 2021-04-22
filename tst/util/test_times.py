""" Tests for utility functions related to manipulating and converting times. """

import pytest

from cubersio.util.times import convert_centiseconds_to_friendly_time


@pytest.mark.parametrize('input_value, expected_friendly_time', [
    ('DNF', 'DNF'),
    (2345, "23.45"),
    (12345, "2:03.45"),
    (13399, "2:13.99"),
    ("12345", "2:03.45")
])
def test_convert_centiseconds_to_friendly_time(input_value, expected_friendly_time):
    assert convert_centiseconds_to_friendly_time(input_value) == expected_friendly_time
