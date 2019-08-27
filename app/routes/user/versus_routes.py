""" Routes related to comparing results between users. """

from http import HTTPStatus
import json

from flask import render_template
from flask_login import current_user

from app import app
from app.util.events.resources import sort_event_id_name_map_by_global_sort_order
from app.persistence.events_manager import get_events_id_name_mapping
from app.persistence.user_manager import get_user_by_username, get_all_active_usernames
from app.persistence.user_site_rankings_manager import get_site_rankings_for_user
from app.persistence.user_results_manager import get_user_completed_solves_count,\
    get_user_medals_count
from app.persistence.comp_manager import get_user_participated_competitions_count

# -------------------------------------------------------------------------------------------------

NO_SUCH_USER_ERR_MSG = "Oops, can't find a user with username '{}'"

EVENT_NOT_PARTICIPATED = (None, None, None, None)

# -------------------------------------------------------------------------------------------------
# Standard routes, to be removed once React components + API endpoints are finalized and being used
# -------------------------------------------------------------------------------------------------

@app.route('/vs/<username>')
def me_versus_other(username):
    """ A route for displaying user results head-to-head with the current user. """

    # TODO here and below, implement proper error-handling

    user1 = current_user
    user2 = get_user_by_username(username)
    if not user2:
        return NO_SUCH_USER_ERR_MSG.format(username), HTTPStatus.NOT_FOUND

    return __render_versus_page_for_users(user1, user2)


def __render_versus_page_for_users(user1, user2):
    """ Renders and returns a user versus page for the specified two users. """

    # Get a map of event ID to event name, to facilitate rendering the template.
    # Sort it by the global sort order so the event records table has the same ordering
    # as everywhere else.
    event_id_name_map = get_events_id_name_mapping()
    event_id_name_map = sort_event_id_name_map_by_global_sort_order(event_id_name_map)

    # Get site rankings info for both users
    # Get users' medal counts, number of total solves, number of competitions participated in
    rankings1, user1_stats = __get_versus_page_info_for_user(user1)
    rankings2, user2_stats = __get_versus_page_info_for_user(user2)

    # Remove any events which neither user has participated in
    __remove_events_not_participated_in(event_id_name_map, rankings1, rankings2)

    return render_template("user/versus.html", username1=current_user.username, username2=user2.username,
        rankings1=rankings1, rankings2=rankings2, event_id_name_map=event_id_name_map,
        user1_stats=user1_stats, user2_stats=user2_stats)

# -------------------------------------------------------------------------------------------------
# API endpoints
# -------------------------------------------------------------------------------------------------

@app.route('/api/usernames/')
def usernames():
    """ A route for retrieving a list of usernames for all active users. """

    return json.dumps(get_all_active_usernames())


@app.route('/api/site_stats/<username>/')
def user_site_stats(username):
    """ A route for retrieving data related to a user's usage of the site. Returns a JSON-serialized
    dictionary of the form:
    { event_id: [single, single_site_ranking, average, average_site_ranking] } """

    user = get_user_by_username(username)
    if not user:
        return NO_SUCH_USER_ERR_MSG.format(username), HTTPStatus.NOT_FOUND

    return json.dumps(__get_user_site_rankings(user.id))


@app.route('/api/site_rankings/<username>/')
def user_site_rankings(username):
    """ A route for retrieving data related to a user's PBs for all events. Returns a JSON-serialized
    dictionary of the form:
    { event_id: [single, single_site_ranking, average, average_site_ranking] } """

    # TODO: format the values at indices 0 and 3 to be user-friendly representations of the results.
    #
    # Right now they are just the raw centiseconds, encoded MBLD, or "centi-moves" FMC values
    #
    # Further thinking... should I just format those for user-friendly display when I save them
    # to the database? I don't think we use the raw results times anywhere, and we're just wasting time
    # converting all of them each time we display them.

    user = get_user_by_username(username)
    if not user:
        return NO_SUCH_USER_ERR_MSG.format(username), HTTPStatus.NOT_FOUND

    return json.dumps(__get_user_site_rankings(user.id))

# -------------------------------------------------------------------------------------------------

def __get_versus_page_info_for_user(user):
    """ Retrieves all the info needed to render the versus page for a single user. Returns a
    tuple of the form: () """

    return __get_user_site_rankings(user.id), __get_user_site_stats(user.id)


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
    # even events they haven't participated in, in case the other user has done that event.
    for event_id in event_id_name_map.keys():
        if event_id not in site_rankings.keys():
            site_rankings[event_id] = EVENT_NOT_PARTICIPATED

    return site_rankings


def __get_user_site_stats(user_id):
    """ Retrieves a user's stats related to their usage of the site: """

    medals_count = get_user_medals_count(user_id)
    return {
        'solve_count':  get_user_completed_solves_count(user_id),
        'comps_count':  get_user_participated_competitions_count(user_id),
        'medals_count': {
            'gold':   medals_count[0],
            'silver': medals_count[1],
            'bronze': medals_count[2]
        },
    }


def __remove_events_not_participated_in(event_id_name_map, rankings1, rankings2):
    """ Checks both sets of user rankings, and removes the entries for events that neither user has
    participated in. """

    # Determine any events that both users haven't participated in
    event_ids_to_remove = list()
    for event_id in event_id_name_map.keys():

        # This is a blank entry we added below in __get_user_site_rankings when retrieving
        # the site rankings to ensure both users have a record if at least one does
        ranks1_empty = rankings1[event_id] == EVENT_NOT_PARTICIPATED
        ranks2_empty = rankings2[event_id] == EVENT_NOT_PARTICIPATED

        # This is an entry that existed in the site rankings for some reason, but with an
        # empty result, indicating the user hasn't actually participated.
        # TODO: figure out why this is happening. Bad devo data?
        ranks1_empty_2 = rankings1[event_id][0] == rankings1[event_id][2] == ''
        ranks2_empty_2 = rankings2[event_id][0] == rankings2[event_id][2] == ''

        if (ranks1_empty or ranks1_empty_2) and (ranks2_empty or ranks2_empty_2):
            event_ids_to_remove.append(event_id)

    # Remove any events from the rankings and from the event_id_name_map
    for event_id in event_ids_to_remove:
        del rankings1[event_id]
        del rankings2[event_id]
        del event_id_name_map[event_id]
