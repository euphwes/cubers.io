""" WCA auth routes. """
# pylint: disable=invalid-name

from flask import request, redirect, url_for, render_template
from flask_login import current_user, login_user

from cubersio import app
from cubersio.persistence.user_manager import update_or_create_user_for_wca, add_wca_info_to_user,\
    get_user_by_wca_id

from cubersio.integrations.wca import get_wca_auth_url, get_wca_access_token_from_auth_code,\
    get_wca_id_from_access_token, WCAAuthException

from . import __encrypt_state, __decrypt_state, __OAUTH_CODE, __OAUTH_DENIED, __OAUTH_ERROR,\
    __OAUTH_STATE, __OAUTH_INVALID_GRANT, __OAUTH_STATE_ARG_DELIMITER

# -------------------------------------------------------------------------------------------------

__WCA_ASSOC_STATE_PREFIX = 'wca_assoc'
__WCA_ASSOC_STATE_FORMAT = '{assoc_state_prefix}|{username}'

__WCA_LOGIN_STATE_PREFIX = 'login'

__ERR_WRONG_USER = 'Oops! This WCA association attempt appears to be for a different user.'

__ERR_ACCOUNT_ALREADY_EXISTS = 'An account for WCA user {} already exists! '
__ERR_ACCOUNT_ALREADY_EXISTS += 'Support for merging accounts is coming soon.'

__ERR_NO_WCA_ID = "You don't have a WCA ID. "
__ERR_NO_WCA_ID += "Please try logging in again after you have been assigned a WCA ID."

__ERR_UNKNOWN = 'Something went wrong, sorry! Please show this to /u/euphwes: {}'

# -------------------------------------------------------------------------------------------------

def __get_oauth_state_for_WCA_association(username):
    """ Returns a state to pass to WCA OAuth that indicates upon return that we're attempting
    to associate the WCA login with the currently logged-in user. """

    state = __WCA_ASSOC_STATE_FORMAT.format(assoc_state_prefix=__WCA_ASSOC_STATE_PREFIX,
                                            username=username)

    return __encrypt_state(state)


def __handle_login_state(_, wca_id, token):
    """ Handle a successful WCA OAuth call where the state indicates this is a login. """

    user = update_or_create_user_for_wca(wca_id, token)
    login_user(user, True)

    return redirect(url_for('index'))


def __handle_assoc_state(state_params, wca_id, token):
    """ Handle a successful WCA OAuth call where the state indicates this is a WCA account
    association. """

    # It's not valid to handle an account associaton attempt if the user isn't already logged in
    if not current_user.is_authenticated:
        return redirect(url_for('prompt_login'))

    # If the user's logged in already, it's in a Reddit account.
    # Double-check the currently logged-in user is the same username that kicked off the request.
    reddit_user_to_associate = state_params[0]
    if not current_user.username == reddit_user_to_associate:
        return render_template('error.html', error_message=__ERR_WRONG_USER)

    # Make sure we don't already have an account for this WCA ID
    if get_user_by_wca_id(wca_id):
        msg = __ERR_ACCOUNT_ALREADY_EXISTS.format(wca_id)
        return render_template('error.html', error_message=msg)

    # Associate the WCA login info with the current user, and redirect to their profile
    add_wca_info_to_user(current_user.username, wca_id, token)
    return redirect(url_for('profile', username=current_user.username))


__STATE_HANDLERS = {
    __WCA_LOGIN_STATE_PREFIX: __handle_login_state,
    __WCA_ASSOC_STATE_PREFIX: __handle_assoc_state
}

# -------------------------------------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------------------------------------

@app.route('/wca_login')
def wca_login():
    """ Log in a user via WCA. """

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    state = __encrypt_state(__WCA_LOGIN_STATE_PREFIX)
    return redirect(get_wca_auth_url(state=state))


@app.route('/wca_assoc')
def wca_assoc():
    """ Associate the logged-in user with a WCA account. """

    if not current_user.is_authenticated:
        return redirect(url_for('prompt_login'))

    state = __get_oauth_state_for_WCA_association(current_user.username)
    return redirect(get_wca_auth_url(state=state))


@app.route('/wca_authorize')
def wca_authorize():
    """ Handle the callback from WCA's OAuth. Create a user if necessary, update their refresh
    token, and log the user in. """

    # Check if the user denied the OAuth request, and handle if necessary
    error = request.args.get(__OAUTH_ERROR, None)
    if error == __OAUTH_DENIED:
        return redirect(url_for('denied'))

    # Extract the state and code from the auth return
    state = __decrypt_state(request.args.get(__OAUTH_STATE))
    code = request.args.get(__OAUTH_CODE)

    # Pull the WCA username and access token via the access code
    try:
        token = get_wca_access_token_from_auth_code(code)
        wca_id = get_wca_id_from_access_token(token)

        if not wca_id:
            return render_template('error.html', error_message=__ERR_NO_WCA_ID)

    except WCAAuthException as wca_error:
        err = str(wca_error)

        # "invalid_grant" indicates hitting the access token url with an expired auth code,
        # probably just me refreshing on /wca_authorize?... during testing
        if err == __OAUTH_INVALID_GRANT:
            return redirect(url_for('wca_login'))

        return render_template('error.html', error_message=__ERR_UNKNOWN.format(err))

    # Split the state string into its component pieces
    # First is the state itself, remainder are the args, if any
    split_state = state.split(__OAUTH_STATE_ARG_DELIMITER)
    state, state_params = split_state[0], split_state[1:]

    # Handle the remainder of the authorized request by acting on the state
    return __STATE_HANDLERS[state](state_params, wca_id, token)
