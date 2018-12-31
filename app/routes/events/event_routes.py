""" Routes related to displaying competition results. """

from flask import render_template, redirect
from flask_login import current_user

from app import CUBERS_APP
from app.persistence.user_manager import get_comp_userlist_blacklist_map
from app.persistence.user_results_manager import get_ordered_users_pb_singles_for_event_for_event_results,\
    get_ordered_users_pb_averages_for_event_for_event_results
from app.persistence.comp_manager import get_events_id_name_mapping, get_event_by_name

from ranking import Ranking

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route('/event/<event_name>/')
def event_results(event_name):
    """ A route for showing the global top results for a specific event. """

    # for some reason the urlencode and urldecode isn't handling forward slash properly
    event_name = event_name.replace('%2F', '/')

    event = get_event_by_name(event_name)
    if not event:
        return "oops " + event_name

    blacklist_mapping = get_comp_userlist_blacklist_map()

    singles = get_ordered_users_pb_singles_for_event_for_event_results(event.id, blacklist_mapping)
    singles = convert_to_pbRecords(singles)
    singles_values = list()
    for single in singles:
        try:
            singles_values.append(int(single.pb))
        except:
            singles_values.append(9999999999999)
    ranked_singles = list(Ranking(singles_values, start=1, reverse=True))
    for i, single in enumerate(singles):
        single.rank = ranked_singles[i][0]

    averages = get_ordered_users_pb_averages_for_event_for_event_results(event.id, blacklist_mapping)
    averages = convert_to_pbRecords(averages)
    averages_values = list()
    for average in averages:
        try:
            averages_values.append(int(average.pb))
        except:
            averages_values.append(9999999999999)
    ranked_averages = list(Ranking(averages_values, start=1, reverse=True))
    for i, average in enumerate(averages):
        average.rank = ranked_averages[i][0]

    title = "{} Records".format(event_name)

    return render_template("event/results.html", event_id=event.id, event_name=event_name,\
        singles=singles, averages=averages, alternative_title=title)

# -------------------------------------------------------------------------------------------------

class PbRecord():
    def __init__(self, user_id, pb, comp_id, username, comp_title):
        self.user_id = user_id
        self.pb = pb
        self.comp_id = comp_id
        self.username = username
        self.comp_title = comp_title
        self.rank = -1

def convert_to_pbRecords(ordered_pbs_tuples):
    pb_records = list()
    for user_id, single, comp_id, username, comp_title in ordered_pbs_tuples:
        pb_records.append(PbRecord(user_id, single, comp_id, username, comp_title))
    return pb_records