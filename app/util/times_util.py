""" Utility functions for working with times. """

#pylint: disable=C0103
def convert_centiseconds_to_friendly_time(centiseconds):
    """ Converts centiseconds to a human-readable friendly time.
    Ex: 2345 --> 23.45
    Ex: 12345 --> 2:03.45 """

    secs = centiseconds / 100.0

    if secs < 60:
        return '{0:.2f}'.format(secs)

    minutes = int(secs // 60)
    seconds = '{0:.2f}'.format(secs % 60).zfill(5)

    return '{}:{}'.format(minutes, seconds)

# -------------------------------------------------------------------------------------------------
# TODO: Figure out if stuff below is needed. Does it belong in the scripts source? If so, doesn't
# belong directly here in the web app
# -------------------------------------------------------------------------------------------------

def convert_min_sec(time):
    """ Convert friendly time to seconds. Ex: 1:23:45 --> 83.45. """
    try:
        if ":" not in time:
            return float(time)

        mins = (int)(time[0: time.index(":")])
        secs = (int)(time[time.index(":") + 1: time.index(".")])
        dec = (int)(time[time.index(".") + 1: time.index(".") + 3])

        secs += mins * 60

        if dec < 10:
            return float(str(secs) + ".0" + str(dec))
        else:
            return float(str(secs) + "." + str(dec))

    except ValueError:
        print("Value error! ", time)
        return "convert error"
