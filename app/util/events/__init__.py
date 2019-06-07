""" Generic events resources stuff goes here. """

from app.util.times import convert_centiseconds_to_friendly_time

# -------------------------------------------------------------------------------------------------

def build_mbld_results(coded_value):
    """ Builds and returns a user-friendly representation of MBLD results from the coded integer
    representation. """

    coded_result = str(coded_value)
    while len(coded_result) < 8:
        coded_result = '0' + coded_result

    # coded results format is XXYYYYZZ
    # where XX   = (99 - number of points)
    # where YYYY = elapsed seconds (4 digits, padded with insignificant zeros)
    # where ZZ   = number missed (2 digits, padded with insignificant zeros)
    xx   = int(coded_result[0:2])
    yyyy = int(coded_result[2:6])
    zz   = int(coded_result[6:])

    # math. woohoo.
    num_attempted  = 99 - xx + (2 * (zz))
    num_successful = num_attempted - zz

    time = convert_centiseconds_to_friendly_time(yyyy * 100)
    time_no_fractions = time[:len(time) - 3]

    return '{}/{} {}'.format(num_successful, num_attempted, time_no_fractions)
