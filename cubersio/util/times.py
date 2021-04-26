""" Utility functions for working with times. """
from typing import Union


def convert_centiseconds_to_friendly_time(centiseconds: Union[int, str]) -> str:
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
