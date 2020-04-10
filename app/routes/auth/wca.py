""" WCA auth routes. """

from . import __encrypt_state, __decrypt_state

from flask import request, redirect, url_for
from flask_login import current_user, login_user

from app import app
from app.persistence.user_manager import update_or_create_user_for_wca, add_wca_info_to_user,\
    get_user_by_wca_id

from app.util.wca import get_wca_auth_url, get_wca_access_token_from_auth_code,\
    get_wca_id_from_access_token, WCAAuthException

# -------------------------------------------------------------------------------------------------

STATE_WCA_ASSOC_HEADER = 'wca_assoc'

# -------------------------------------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------------------------------------

@app.route('/wca_login')
def wca_login():
    """ Log in a user via WCA. """

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    state = __encrypt_state('login')
    return redirect(get_wca_auth_url(state=state))


@app.route('/wca_assoc')
def wca_assoc():
    """ Associate the logged-in user with a WCA account. """

    if not current_user.is_authenticated:
        return redirect(url_for('prompt_login'))

    state = "{}|{}".format(STATE_WCA_ASSOC_HEADER, current_user.username)
    state = __encrypt_state(state)

    return redirect(get_wca_auth_url(state=state))


@app.route('/wca_authorize')
def wca_authorize():
    """ Handle the callback from WCA's OAuth. Create a user if necessary, update their refresh
    token, and log the user in. """

    error = request.args.get('error', None)
    if error == 'access_denied':
        return redirect(url_for('denied'))

    auth_code = request.args.get('code')
    state = __decrypt_state(request.args.get('state'))

    try:
        access_token = get_wca_access_token_from_auth_code(auth_code)
    except WCAAuthException as wca_error:
        err = str(wca_error)

        # "invalid_grant" indicates hitting the access token url with an expired auth code,
        # probably just me refreshing on /wca_authorize?... during testing
        if err == 'invalid_grant':
            return redirect(url_for('wca_login'))

        return "Something went wrong, sorry! Please show this to /u/euphwes: " + str(wca_error)

    wca_id = get_wca_id_from_access_token(access_token)

    if state.startswith(STATE_WCA_ASSOC_HEADER):
        return complete_wca_assoc(state, wca_id, access_token)

    user = update_or_create_user_for_wca(wca_id, access_token)

    login_user(user, True)

    return redirect(url_for('index'))


def complete_wca_assoc(oauth_state, wca_id, wca_access_token):
    """ Completes WCA account association following a successful WCA OAuth login. """

    # state should look like: STATE_WCA_ASSOC_HEADER|username

    if not current_user.is_authenticated:
        return redirect(url_for('prompt_login'))

    reddit_user_to_associate = oauth_state.split('|')[1]

    if not current_user.username == reddit_user_to_associate:
        return 'Oops! This WCA association attempt appears to be for a different user.'

    prexisting_wca_user = get_user_by_wca_id(wca_id)
    if prexisting_wca_user:
        return "An account for WCA ID {} already exists! Support for merging accounts coming soon.".format(wca_id)

    add_wca_info_to_user(current_user.username, wca_id, wca_access_token)
    return redirect(url_for('profile', username=current_user.username))
