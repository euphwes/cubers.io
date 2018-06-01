""" Routes related to authentication. """

from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_user, logout_user

from app import CUBERS_APP
from app.persistence.user_manager import update_or_create_user, get_all_users

from app.util.reddit_util import get_username_refresh_token_from_code, get_user_auth_url
# -------------------------------------------------------------------------------------------------




@CUBERS_APP.route("/logout")
def logout():
    """ Log out the current user. """
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('index'))


@CUBERS_APP.route('/login')
def login():
    """ Log in a user. """

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return redirect(get_user_auth_url())


@CUBERS_APP.route('/authorize')
def authorize():
    """ Handle the callback from Reddit's OAuth. Create a user if necessary, update their refresh
    token, and log the user in. """

    #TODO: handle error=access_denied meaning user decline OAuth
    # error = request.args.get('error')
    
    auth_code = request.args.get('code')

    username, refresh_token = get_username_refresh_token_from_code(auth_code)
    user = update_or_create_user(username, refresh_token)

    login_user(user, True)

    return redirect(url_for('index'))

