""" Routes related to comparing results between users. """

from flask import render_template, redirect, url_for
from flask_login import current_user

from http import HTTPStatus

from app import app
from app.business.user_history import get_user_competition_history
from app.persistence.comp_manager import get_user_participated_competitions_count
from app.persistence.user_manager import get_user_by_username, verify_user, unverify_user,\
    set_perma_blacklist_for_user, unset_perma_blacklist_for_user, get_user_by_id
from app.persistence.user_results_manager import get_user_completed_solves_count
from app.persistence.events_manager import get_events_id_name_mapping
from app.persistence.user_site_rankings_manager import get_site_rankings_for_user

# -------------------------------------------------------------------------------------------------

LOG_NO_SUCH_USER = "Oops, can't find a user with username '{}'"

# -------------------------------------------------------------------------------------------------

@app.route('/vs/<other_username>')
def vs_user(other_username):
    """ A route for displaying user results head-to-head with the current user. """

    return render_template("user/versus.html", user1=current_user.username, user2=other_username)


@app.route('/api/pbs/<username>/')
def user_pbs(username):
    """ A route for retrieving data related to a user's PBs for all events. """

    user = get_user_by_username(username)
    if not user:
        return LOG_NO_SUCH_USER.format(username), HTTPStatus.NOT_FOUND
