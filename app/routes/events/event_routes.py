""" Routes related to displaying competition results. """

from flask import render_template

from app import CUBERS_APP
from app.business.rankings import get_ordered_pb_averages_for_event,\
    get_ordered_pb_singles_for_event
from app.persistence.comp_manager import get_event_by_name

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route('/event/<event_name>/')
def event_results(event_name):
    """ A route for showing the global top results for a specific event. """

    # for some reason the urlencode and urldecode isn't handling forward slash properly
    event_name = event_name.replace('%2F', '/')

    event = get_event_by_name(event_name)
    if not event:
        return "I don't know what {} is.".format(event_name)

    singles = get_ordered_pb_singles_for_event(event.id)
    averages = get_ordered_pb_averages_for_event(event.id)

    title = "{} Records".format(event_name)

    return render_template("event/results.html", event_id=event.id, event_name=event_name,\
        singles=singles, averages=averages, alternative_title=title)
