""" Routes related to authentication. """

from base64 import urlsafe_b64decode, urlsafe_b64encode

from flask import request, redirect, url_for, render_template
from flask_login import current_user, login_user, logout_user

from app import app
from app.persistence import comp_manager
from app.persistence.user_manager import update_or_create_user_for_reddit,\
    update_or_create_user_for_wca, add_wca_info_to_user, get_user_by_wca_id,\
    add_reddit_info_to_user, get_user_by_reddit_id

from app.util.reddit import get_username_refresh_token_from_code, get_reddit_auth_url,\
    get_app_account_auth_url

from app.util.wca import get_wca_auth_url, get_wca_access_token_from_auth_code,\
    get_wca_id_from_access_token, WCAAuthException

from app.util.simplecrypt import encrypt, decrypt

# -------------------------------------------------------------------------------------------------

STATE_WCA_ASSOC_HEADER = 'wca_assoc'
STATE_REDDIT_ASSOC_HEADER = 'reddit_assoc'

SECRET_KEY = app.config['FLASK_SECRET_KEY']

def __encrypt_oauth_state(state):
    """ Encrypts a given string using simple-crypt, and then base64 encodes the value to make it
    url-safe. """

    return urlsafe_b64encode(encrypt(SECRET_KEY, state))


def __decrypt_oauth_state(state):
    """ Base64 decodes a given string into a byte array, which is decrypted using simple-crypt to
    return the original string and converted back to a string. """

    return decrypt(SECRET_KEY, urlsafe_b64decode(state)).decode('utf-8')

# -------------------------------------------------------------------------------------------------
# Reddit auth routes
# -------------------------------------------------------------------------------------------------

@app.route('/reddit_login')
def reddit_login():
    """ Log in a user via Reddit. """

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    return redirect(get_reddit_auth_url(state=__encrypt_oauth_state('login')))


@app.route('/reddit_assoc')
def reddit_assoc():
    """ Associate the logged-in user with a Reddit account. """

    if not current_user.is_authenticated:
        return redirect(url_for('prompt_login'))

    state = "{}|{}".format(STATE_REDDIT_ASSOC_HEADER, current_user.username)
    state = __encrypt_oauth_state(state)

    return redirect(get_reddit_auth_url(state=state))


@app.route('/authorize')
def reddit_authorize():
    """ Handle the callback from Reddit's OAuth. Create a user if necessary, update their refresh
    token, and log the user in. """

    error = request.args.get('error', None)
    if error == 'access_denied':
        return redirect(url_for('denied'))

    auth_code = request.args.get('code')
    state = __decrypt_oauth_state(request.args.get('state'))

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


# -------------------------------------------------------------------------------------------------
# WCA auth routes
# -------------------------------------------------------------------------------------------------

@app.route('/wca_login')
def wca_login():
    """ Log in a user via WCA. """

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    state = __encrypt_oauth_state('login')
    return redirect(get_wca_auth_url(state=state))


@app.route('/wca_assoc')
def wca_assoc():
    """ Associate the logged-in user with a WCA account. """

    if not current_user.is_authenticated:
        return redirect(url_for('prompt_login'))

    state = "{}|{}".format(STATE_WCA_ASSOC_HEADER, current_user.username)
    state = __encrypt_oauth_state(state)

    return redirect(get_wca_auth_url(state=state))


@app.route('/wca_authorize')
def wca_authorize():
    """ Handle the callback from WCA's OAuth. Create a user if necessary, update their refresh
    token, and log the user in. """

    error = request.args.get('error', None)
    if error == 'access_denied':
        return redirect(url_for('denied'))

    auth_code = request.args.get('code')
    state = __decrypt_oauth_state(request.args.get('state'))

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


# -------------------------------------------------------------------------------------------------
# Common auth routes
# -------------------------------------------------------------------------------------------------

@app.route("/logout")
def logout():
    """ Log out the current user. """

    if current_user.is_authenticated:
        logout_user()

    return redirect(url_for('index'))


@app.route('/denied')
def denied():
    """ For when the user declines OAuth. """

    comp = comp_manager.get_active_competition()
    return render_template('prompt_login/denied.html', current_competition=comp)
