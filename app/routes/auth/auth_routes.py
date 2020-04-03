""" Routes related to authentication. """

from json import loads as json_loads

from flask import request, redirect, url_for, render_template
from flask_login import current_user, login_user, logout_user

from requests import post as post_request, get as get_request

from app import app
from app.persistence import comp_manager
from app.persistence.user_manager import update_or_create_user

from app.util.reddit import get_username_refresh_token_from_code, get_user_auth_url,\
    get_app_account_auth_url

# -------------------------------------------------------------------------------------------------

@app.route("/logout")
def logout():
    """ Log out the current user. """

    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('index'))


@app.route('/login')
def login():
    """ Log in a user. """

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return redirect(get_user_auth_url())


@app.route('/wca_login')
def wca_login():
    """ Log in a user via WCA. """

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    return redirect("https://www.worldcubeassociation.org/oauth/authorize?client_id= ?? &redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fwca_authorize&response_type=code&scope=public")


@app.route('/wca_authorize')
def wca_authorize():
    """ TODO """

    error = request.args.get('error', None)
    if error == 'access_denied':
        return redirect(url_for('denied'))

    auth_code = request.args.get('code')

    payload = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'client_id': '',
        'client_secret': '',
        'redirect_uri': 'http://localhost:5000/wca_authorize',
    }

    url = 'https://www.worldcubeassociation.org/oauth/token'

    response = post_request(url, data=payload)
    access_token = json_loads(response.text)['access_token']

    # TODO or check for error, maybe redirect back to login

    headers = {"Authorization": "Bearer " + access_token}
    me_data = get_request("https://www.worldcubeassociation.org/api/v0/me", headers=headers)

    return str(me_data.json())


@app.route('/admin_login')
def admin_login():
    """ Log in a an admin user account.
    HACK alert: this is a workaround to get the app Reddit accounts the privileges required to send PMs.
    It's safe that this is exposed, because if a regular user logs in from here, nothing changes from
    their POV except it asks for one more permission. It doesn't otherwise give the regular user account
    any special powers or anything. TODO: figure out the right way to do this. """

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return redirect(get_app_account_auth_url())


@app.route('/authorize')
def authorize():
    """ Handle the callback from Reddit's OAuth. Create a user if necessary, update their refresh
    token, and log the user in. """

    error = request.args.get('error', None)
    if error == 'access_denied':
        return redirect(url_for('denied'))

    auth_code = request.args.get('code')

    username, refresh_token = get_username_refresh_token_from_code(auth_code)
    user = update_or_create_user(username, refresh_token)

    login_user(user, True)

    if comp_manager.get_active_competition():
        return redirect(url_for('index'))

    return "Successfully logged in as {}. There are no competitions created yet. Go make one!".format(username)


@app.route('/denied')
def denied():
    """ For when the user declines Reddit OAuth. """

    comp = comp_manager.get_active_competition()
    return render_template('prompt_login/denied.html', current_competition=comp)
