from cubersio.util.times import convert_centiseconds_to_friendly_time


def build_mbld_results(coded_value):
    """ Builds and returns a user-friendly representation of MBLD results from the coded integer
    representation. """

    coded_result = str(coded_value)

    if coded_result == 'DNF':
        return 'DNF'

    num_successful, num_attempted, seconds = __parse_mbld_coded_value(coded_result)

    time = convert_centiseconds_to_friendly_time(seconds * 100)
    time_no_fractions = time[:len(time) - 3]

    return '{}/{} {}'.format(num_successful, num_attempted, time_no_fractions)


def get_mbld_successful_and_attempted(coded_value):
    """ Takes a coded integer representation of MBLD results, and returns a tuple of
    (num_successful, num_attempted). """

    coded_result = str(coded_value)

    if coded_result == 'DNF':
        return (None, None)

    num_successful, num_attempted, _ = __parse_mbld_coded_value(coded_result)

    return (num_successful, num_attempted)


def get_mbld_total_points(coded_value):
    """ Returns the number of points for the MBLD results. """

    coded_result = str(coded_value)

    if coded_result == 'DNF':
        return 0

    num_successful, num_attempted, _ = __parse_mbld_coded_value(coded_result)

    # 52 attempted, 50 successful = 48 points
    # 50 - (52 - 50)
    # 50 - 2
    # 48

    return num_successful - (num_attempted - num_successful)


def get_mbld_fraction_of_hour_remaining(coded_value):
    """ Returns the fraction of the hour remaining for the MBLD results. """

    coded_result = str(coded_value)

    if coded_result == 'DNF':
        return 0

    _, _, elapsed_seconds = __parse_mbld_coded_value(coded_result)
    elapsed_minutes = elapsed_seconds / 60.0

    return (60 - elapsed_minutes) / 60.0


def __parse_mbld_coded_value(coded_value):
    """ Parses a coded integer representation of MBLD results, returning a tuple of
    (num_successful, num_attempted, time_seconds). """

    while len(coded_value) < 8:
        coded_value = '0' + coded_value

    # coded results format is XXYYYYZZ
    # where XX   = (99 - number of points)
    # where YYYY = elapsed seconds (4 digits, padded with insignificant zeros)
    # where ZZ   = number missed (2 digits, padded with insignificant zeros)
    xx   = int(coded_value[0:2])
    yyyy = int(coded_value[2:6])
    zz   = int(coded_value[6:])

    # math. woohoo.
    num_attempted  = 99 - xx + (2 * (zz))
    num_successful = num_attempted - zz

    return (num_successful, num_attempted, yyyy)