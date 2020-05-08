""" Routes related to displaying event records. """

from collections import namedtuple, OrderedDict
from csv import writer as csv_writer
from io import StringIO

from flask import render_template, make_response
from flask_login import current_user

from app import app
from app.business.rankings import get_ordered_pb_averages_for_event,\
    get_ordered_pb_singles_for_event
from app.persistence.comp_manager import get_event_by_name

# -------------------------------------------------------------------------------------------------

# Container for sum of ranks data
UserPBPair = namedtuple('UserPBPair', ['username', 'single', 'average'])

CSV_HEADERS           = ['Username', 'Single (seconds)', 'Average (seconds)']
CSV_FILENAME_TEMPLATE = '{event_name}_results.csv'
CSV_EMPTY             = ''

# -------------------------------------------------------------------------------------------------

@app.route('/event/<event_name>/')
def event_results(event_name):
    """ A route for showing the global top results for a specific event. """

    event = __safe_get_event(event_name)
    if not event:
        return ("I don't know what {} is.".format(event_name), 404)

    singles  = get_ordered_pb_singles_for_event(event.id)
    averages = get_ordered_pb_averages_for_event(event.id)

    title = "{} Records".format(event.name)

    return render_template("records/event.html", event_id=event.id, event_name=event.name,
                           singles=singles, averages=averages, alternative_title=title,
                           show_admin=current_user.is_admin)


@app.route('/event/<event_name>/export/')
def event_results_export(event_name):
    """ A route for exporting events records in CSV format. """

    event = __safe_get_event(event_name)
    if not event:
        return ("I don't know what {} is.".format(event_name), 404)

    singles  = get_ordered_pb_singles_for_event(event.id)
    averages = get_ordered_pb_averages_for_event(event.id)

    user_pb_dict = __build_user_pb_pairs(singles, averages)

    return __build_csv_output(event.name, user_pb_dict)

# -------------------------------------------------------------------------------------------------

def __safe_get_event(event_name):
    """ Decodes the event name from the URL and retrieves that event. """

    # For some reason the urlencode and urldecode isn't handling forward slash properly
    # and we named the mirror blocks event with a slash...
    event_name = event_name.replace('%2F', '/')
    return get_event_by_name(event_name)


def __scrub_pb_value(value):
    """ Scrubs a PB result value to omit DNFs, and to represent centiseconds as seconds. """

    return int(value) / 100.00 if value and value != 'DNF' else ''


def __build_user_pb_pairs(singles, averages):
    """ Store user PB records per user in a UserPBPair container, so we can include both PB single
    and average for each user in the same line easily. """

    user_pb_dict = OrderedDict()

    # While this looks like it's O(N^2), in fact both of these lists are sorted by result value,
    # and each user is likely to occupy a similar index in both lists. The inner loop across
    # averages will break early as it encounters the matching user
    for pb_single in singles:
        username = pb_single.username
        single  = __scrub_pb_value(pb_single.personal_best)
        average = CSV_EMPTY

        for pb_average in averages:
            if username == pb_average.username:
                average = __scrub_pb_value(pb_average.personal_best)
                break

        user_pb_dict[username] = UserPBPair(username=username, single=single, average=average)

    return user_pb_dict


def __build_csv_output(event_name, user_pb_dict):
    """ Builds a Flask file output response for a CSV containing the PB single and averages for each
    user for the specified event. """

    # Build a StringIO object and use it as the file for the CSV writer
    string_io = StringIO()
    writer = csv_writer(string_io)

    # Write the header
    writer.writerow(CSV_HEADERS)

    # Write the rows for each user's PB single and average
    for username, pb_pair in user_pb_dict.items():
        writer.writerow([username, pb_pair.single, pb_pair.average])

    filename = CSV_FILENAME_TEMPLATE.format(event_name=event_name)
    output = make_response(string_io.getvalue())
    output.headers['Content-Disposition'] = "attachment; filename={}".format(filename)
    output.headers['Content-type'] = "text/csv"

    return output
