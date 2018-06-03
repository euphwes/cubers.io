def convert_min_sec(time):
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


def convert_centiseconds_to_friendly_time(centiseconds):
    """ Converts centiseconds to a human-readable friendly time.
    Ex: 2345 --> 23.45
    Ex: 12345 --> 2:03.45 """

    secs = centiseconds / 100.0

    if secs < 60:
        return '{0:.2f}'.format(secs)

    minutes = int(secs // 60)
    seconds = '{0:.2f}'.format(secs % 60)

    return '{}:{}'.format(minutes, seconds)