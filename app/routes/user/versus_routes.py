""" Routes related to comparing results between users. """

from flask import render_template
from flask_login import current_user

from http import HTTPStatus
import json

from app import app
from app.util.events.resources import sort_event_id_name_map_by_global_sort_order
from app.persistence.events_manager import get_events_id_name_mapping
from app.persistence.user_manager import get_user_by_username
from app.persistence.user_site_rankings_manager import get_site_rankings_for_user

# -------------------------------------------------------------------------------------------------

LOG_NO_SUCH_USER = "Oops, can't find a user with username '{}'"

# -------------------------------------------------------------------------------------------------

@app.route('/vs/<other_username>')
def vs_user(other_username):
    """ A route for displaying user results head-to-head with the current user. """

    # TODO here and below, implement proper error-handling

    event_id_name_map = get_events_id_name_mapping()
    event_id_name_map = sort_event_id_name_map_by_global_sort_order(event_id_name_map)

    other_user = get_user_by_username(other_username)
    if not other_user:
        return LOG_NO_SUCH_USER.format(other_username), HTTPStatus.NOT_FOUND

    rankings1 = __get_user_site_rankings(current_user.id)
    rankings2 = __get_user_site_rankings(other_user.id)

    return render_template("user/versus.html", username1=current_user.username, username2=other_username,
        rankings1=rankings1, rankings2=rankings2, event_id_name_map=event_id_name_map)


@app.route('/api/site_rankings/<username>/')
def user_site_rankings(username):
    """ A route for retrieving data related to a user's PBs for all events. Returns a JSON-serialized
    dictionary of the form event_id: (single, single_site_ranking, average, average_site_ranking) """

    user = get_user_by_username(username)
    if not user:
        return LOG_NO_SUCH_USER.format(username), HTTPStatus.NOT_FOUND

    return json.dumps(__get_user_site_rankings(user.id))

# -------------------------------------------------------------------------------------------------

def __get_user_site_rankings(user_id):
    """ Retrieves a user site rankings record by user id. """

    event_id_name_map = get_events_id_name_mapping()
    site_rankings = dict()

    # See if the user has any recorded site rankings. If they do, extract the data as a dict so we
    # can build their site ranking table
    site_rankings_record = get_site_rankings_for_user(user_id)
    if site_rankings_record:
        site_rankings = site_rankings_record.get_site_rankings_and_pbs(event_id_name_map)

    # Iterate over all events, making sure there's an entry in the user site rankings for everything,
    # even events they haven't participated in
    for event_id in event_id_name_map.keys():
        if event_id not in site_rankings.keys():
            site_rankings[event_id] = (None, None, None, None)

    return site_rankings
