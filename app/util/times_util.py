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
        return "Error"