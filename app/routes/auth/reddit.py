""" Reddit auth routes. """

from flask import request, redirect, url_for
from flask_login import current_user, login_user

from app import app
from app.persistence.user_manager import update_or_create_user_for_reddit,\
    add_reddit_info_to_user, get_user_by_reddit_id

from app.util.reddit import get_username_refresh_token_from_code, get_reddit_auth_url,\
    get_app_account_auth_url

from . import __encrypt_state, __decrypt_state, __OAUTH_CODE, __OAUTH_DENIED, __OAUTH_ERROR,\
    __OAUTH_STATE, __OAUTH_STATE_ARG_DELIMITER

# -------------------------------------------------------------------------------------------------

__REDDIT_ASSOC_STATE_PREFIX = 'reddit_assoc'
__REDDIT_ASSOC_STATE_FORMAT = '{assoc_state_prefix}|{username}'

__REDDIT_LOGIN_STATE_PREFIX = 'login'

_ERR_WRONG_USER = 'Oops! This Reddit association attempt appears to be for a different user.'

_ERR_ACCOUNT_ALREADY_EXISTS = 'An account for Reddit user {} already exists! '
_ERR_ACCOUNT_ALREADY_EXISTS += 'Support for merging accounts is coming soon.'

# -------------------------------------------------------------------------------------------------

def __get_oauth_state_for_reddit_association(username):
    """ Returns a state to pass to Reddit OAuth that indicates upon return that we're attempting
    to associate the Reddit login with the currently logged-in user. """

    state = __REDDIT_ASSOC_STATE_FORMAT.format(assoc_state_prefix=__REDDIT_ASSOC_STATE_PREFIX,
                                               username=username)

    return __encrypt_state(state)


def __handle_login_state(_, reddit_id, token):
    """ Handle a successful Reddit OAuth call where the state indicates this is a login. """

    user = update_or_create_user_for_reddit(reddit_id, token)
    login_user(user, True)

    return redirect(url_for('index'))


def __handle_assoc_state(state_params, reddit_id, token):
    """ Handle a successful Reddit OAuth call where the state indicates this is a Reddit account
    association. """

    # It's not valid to handle an account associaton attempt if the user isn't already logged in
    if not current_user.is_authenticated:
        return redirect(url_for('prompt_login'))

    # If the user's logged in already, it's in a WCA account. Double-check the currently logged-in
    # user is the same username that kicked off the request.
    wca_user_to_associate = state_params[0]
    if not current_user.username == wca_user_to_associate:
        return _ERR_WRONG_USER

    # Make sure we don't already have an account for this Reddit ID
    if get_user_by_reddit_id(reddit_id):
        return _ERR_ACCOUNT_ALREADY_EXISTS.format(reddit_id)

    # Associate the Reddit login info with the current user, and redirect to their profile
    add_reddit_info_to_user(current_user.username, reddit_id, token)
    return redirect(url_for('profile', username=current_user.username))


__STATE_HANDLERS = {
    __REDDIT_LOGIN_STATE_PREFIX: __handle_login_state,
    __REDDIT_ASSOC_STATE_PREFIX: __handle_assoc_state
}

# -------------------------------------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------------------------------------

@app.route('/reddit_login')
def reddit_login():
    """ Log in a user via Reddit. """

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    state = __encrypt_state(__REDDIT_LOGIN_STATE_PREFIX)
    return redirect(get_reddit_auth_url(state))


@app.route('/reddit_assoc')
def reddit_assoc():
    """ Associate the logged-in user with a Reddit account. """

    if not current_user.is_authenticated:
        return redirect(url_for('prompt_login'))

    state = __get_oauth_state_for_reddit_association(current_user.username)
    return redirect(get_reddit_auth_url(state))


@app.route('/authorize')
def reddit_authorize():
    """ Handle the callback from Reddit's OAuth. Create a user if necessary, update their refresh
    token, and log the user in. """

    # Check if the user denied the OAuth request, and handle if necessary
    if request.args.get(__OAUTH_ERROR, None) == __OAUTH_DENIED:
        return redirect(url_for('denied'))

    # Extract the state and code from the auth return
    state = __decrypt_state(request.args.get(__OAUTH_STATE))
    code  = request.args.get(__OAUTH_CODE)

    # Pull the Reddit username and token via the access code
    reddit_id, token = get_username_refresh_token_from_code(code)

    # Split the state string into its component pieces
    # First is the state itself, remainder are the args, if any
    split_state = state.split(__OAUTH_STATE_ARG_DELIMITER)
    state, state_params = split_state[0], split_state[1:]

    # Handle the remainder of the authorized request by acting on the state
    return __STATE_HANDLERS[state](state_params, reddit_id, token)


@app.route('/admin_login')
def admin_login():
    """ Log in an admin user account via Reddit (cubers_io or cubers_io_test). This specific
    login grants Reddit post and edit OAuth permissions. It's safe that this is exposed, because
    if a regular user logs in from here, nothing changes from their POV except it asks for one
    more permission. It doesn't otherwise give the regular user account any admin rights.
    They'll just have post permissions that we don't use. """

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    return redirect(get_app_account_auth_url())
