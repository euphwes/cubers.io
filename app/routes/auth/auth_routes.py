""" Routes related to authentication. """

from flask import request, redirect, url_for, render_template
from flask_login import current_user, login_user, logout_user

from app import app
from app.persistence import comp_manager
from app.persistence.user_manager import update_or_create_user_for_reddit,\
    update_or_create_user_for_wca

from app.util.reddit import get_username_refresh_token_from_code, get_reddit_auth_url,\
    get_app_account_auth_url

from app.util.wca import get_wca_auth_url, get_wca_access_token_from_auth_code,\
    get_wca_id_from_access_token, WCAAuthException

# -------------------------------------------------------------------------------------------------
# Reddit auth routes
# -------------------------------------------------------------------------------------------------

@app.route('/reddit_login')
def reddit_login():
    """ Log in a user via Reddit. """

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    return redirect(get_reddit_auth_url())


@app.route('/reddit_assoc')
def reddit_assoc():
    """ Associate the logged-in user with a Reddit account. """

    # TODO

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    return redirect(get_reddit_auth_url())


@app.route('/authorize')
def reddit_authorize():
    """ Handle the callback from Reddit's OAuth. Create a user if necessary, update their refresh
    token, and log the user in. """

    error = request.args.get('error', None)
    if error == 'access_denied':
        return redirect(url_for('denied'))

    auth_code = request.args.get('code')

    username, refresh_token = get_username_refresh_token_from_code(auth_code)
    user = update_or_create_user_for_reddit(username, refresh_token)

    login_user(user, True)

    return redirect(url_for('index'))


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

    return redirect(get_wca_auth_url())


@app.route('/wca_assoc')
def wca_assoc():
    """ Associate the logged-in user with a WCA account. """

    # TODO

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    return redirect(get_wca_auth_url())


@app.route('/wca_authorize')
def wca_authorize():
    """ Handle the callback from WCA's OAuth. Create a user if necessary, update their refresh
    token, and log the user in. """

    error = request.args.get('error', None)
    if error == 'access_denied':
        return redirect(url_for('denied'))

    auth_code = request.args.get('code')

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
    user = update_or_create_user_for_wca(wca_id, access_token)

    login_user(user, True)

    return redirect(url_for('index'))


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
