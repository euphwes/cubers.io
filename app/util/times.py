""" Utility functions for working with times. """

# -------------------------------------------------------------------------------------------------

def convert_fmc_centimoves_to_moves(centimoves):
    """ Converts 'centimoves' to moves for FMC, since FMC results are stored a hundreths of a unit
    in order to not deviate from how every other event stores data. """

    try:
        # Ensure that if the input isn't already an int, and can be converted to an int, it is
        centimoves = int(centimoves)
    except ValueError:
        pass

    # if it's still a string here, it's probably a DNF result, just pass that back
    if isinstance(centimoves, str):
        return centimoves

    return str(centimoves / 100)


def convert_centiseconds_to_friendly_time(centiseconds):
    """ Converts centiseconds to a human-readable friendly time.
    Ex: 2345 --> 23.45
    Ex: 12345 --> 2:03.45 """

    try:
        # Ensure that if the input isn't already an int, and can be converted to an int, it is
        centiseconds = int(centiseconds)
    except ValueError:
        pass

    # if it's still a string here, it's probably a DNF result, just pass that back
    if isinstance(centiseconds, str):
        return centiseconds

    secs = centiseconds / 100.0

    if secs < 60:
        return '{0:.2f}'.format(secs)

    minutes = int(secs // 60)
    seconds = '{0:.2f}'.format(secs % 60).zfill(5)

    return '{}:{}'.format(minutes, seconds)


def convert_seconds_to_friendly_time(seconds):
    """ Converts seconds to human-readable friendly time. """

    return convert_centiseconds_to_friendly_time(seconds * 100)
