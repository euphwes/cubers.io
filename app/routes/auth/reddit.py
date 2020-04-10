""" Reddit auth routes. """

from . import __encrypt_state, __decrypt_state

from flask import request, redirect, url_for
from flask_login import current_user, login_user

from app import app
from app.persistence.user_manager import update_or_create_user_for_reddit,\
    add_reddit_info_to_user, get_user_by_reddit_id

from app.util.reddit import get_username_refresh_token_from_code, get_reddit_auth_url,\
    get_app_account_auth_url

# -------------------------------------------------------------------------------------------------

STATE_REDDIT_ASSOC_HEADER = 'reddit_assoc'

# -------------------------------------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------------------------------------

@app.route('/reddit_login')
def reddit_login():
    """ Log in a user via Reddit. """

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    return redirect(get_reddit_auth_url(state=__encrypt_state('login')))


@app.route('/reddit_assoc')
def reddit_assoc():
    """ Associate the logged-in user with a Reddit account. """

    if not current_user.is_authenticated:
        return redirect(url_for('prompt_login'))

    state = "{}|{}".format(STATE_REDDIT_ASSOC_HEADER, current_user.username)
    state = __encrypt_state(state)

    return redirect(get_reddit_auth_url(state=state))


@app.route('/authorize')
def reddit_authorize():
    """ Handle the callback from Reddit's OAuth. Create a user if necessary, update their refresh
    token, and log the user in. """

    error = request.args.get('error', None)
    if error == 'access_denied':
        return redirect(url_for('denied'))

    auth_code = request.args.get('code')
    state = __decrypt_state(request.args.get('state'))

    reddit_id, refresh_token = get_username_refresh_token_from_code(auth_code)

    if state.startswith(STATE_REDDIT_ASSOC_HEADER):
        return complete_reddit_assoc(state, reddit_id, refresh_token)

    user = update_or_create_user_for_reddit(reddit_id, refresh_token)

    login_user(user, True)

    return redirect(url_for('index'))


def complete_reddit_assoc(oauth_state, reddit_id, reddit_token):
    """ Completes Reddit account association following a successful Reddit OAuth login. """

    # state should look like: STATE_REDDIT_ASSOC_HEADER|username

    if not current_user.is_authenticated:
        return redirect(url_for('prompt_login'))

    wca_user_to_associate = oauth_state.split('|')[1]

    if not current_user.username == wca_user_to_associate:
        return 'Oops! This Reddit association attempt appears to be for a different user.'

    prexisting_reddit_user = get_user_by_reddit_id(reddit_id)
    if prexisting_reddit_user:
        return "An account for Reddit user {} already exists! Support for merging accounts coming soon.".format(reddit_id)

    add_reddit_info_to_user(current_user.username, reddit_id, reddit_token)
    return redirect(url_for('profile', username=current_user.username))


@app.route('/admin_login')
def admin_login():
    """ Log in an admin user account via Reddit.

    HACK alert: this is a workaround to get the app Reddit accounts the privileges required to send
    PMs. It's safe that this is exposed, because if a regular user logs in from here, nothing
    changes from their POV except it asks for one more permission. It doesn't otherwise give the
    regular user account any special powers or anything.

    TODO: figure out the right way to do this. """

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    return redirect(get_app_account_auth_url())
