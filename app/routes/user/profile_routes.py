""" Routes related to displaying competition results. """

from flask import render_template, redirect
from flask_login import current_user

from app import CUBERS_APP
from app.persistence.user_manager import get_user_by_username
from app.persistence.user_results_manager import get_user_competition_history

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route('/u/<username>/')
def profile(username):
    """ A route for showing a user's profile. """

    user = get_user_by_username(username)
    if not user:
        return "oops"

    return str(get_user_competition_history(user))
