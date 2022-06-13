""" Functions related to MBLD results. """

from typing import Union

from cubersio.util.times import convert_centiseconds_to_friendly_time


class MbldSolve:
    """ A representation of an MBLD solve, including number of attempted and successful cubes, seconds elapsed, total
    points, and string representation of results. """

    def __init__(self, coded_value: Union[str, int]):
        coded_value = str(coded_value)

        self.is_dnf = coded_value == 'DNF'
        if self.is_dnf:
            self.points = 0
            self.sort_value = 0
            return

        # The coded value must always be an 8-digit value
        while len(coded_value) < 8:
            coded_value = '0' + coded_value

        # The format of a coded solve is XXYYYYZZ
        #   XX   = (99 - number of points)
        #   YYYY = elapsed seconds (4 digits, padded with insignificant zeros)
        #   ZZ   = number missed (2 digits, padded with insignificant zeros)
        xx = int(coded_value[0:2])
        yyyy = int(coded_value[2:6])
        zz = int(coded_value[6:])

        self.attempted = 99 - xx + (2 * zz)
        self.successful = self.attempted - zz
        self.seconds = yyyy

        # Calculate and store the number of points this result is worth
        self.points = self.successful - (self.attempted - self.successful)

        # Calculate and store the fractional hour remaining in this attempt
        elapsed_minutes = self.seconds / 60.0
        self.fractional_hour_remaining = (60 - elapsed_minutes) / 60.0

        # For sorting and comparing MBLD results, use combined points + fraction of hour remaining
        # For tied points, higher fraction of hour remaining wins (because less time was used in the attempt)
        self.sort_value = self.points + self.fractional_hour_remaining

    def __str__(self):
        if self.is_dnf:
            return 'DNF'

        time = convert_centiseconds_to_friendly_time(self.seconds * 100)
        time_no_fractions = time[:len(time) - 3]
        return '{}/{} {}'.format(self.successful, self.attempted, time_no_fractions)
