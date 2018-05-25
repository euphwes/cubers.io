""" Routes related to authentication. """

from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_user, logout_user

from app import CUBERS_APP, DB
from app.models import User

from app.util.reddit_util import get_username_refresh_token_from_code, get_user_auth_url

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route('/')
@CUBERS_APP.route('/index')
def index():
    if current_user.is_authenticated:
        users = User.query.all()
        return render_template('comp.html', users=users)

    return render_template('index.html')


@CUBERS_APP.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('index'))


@CUBERS_APP.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return redirect(get_user_auth_url())


@CUBERS_APP.route('/authorize')
def authorize():
    """ """

    #TODO: handle error=access_denied meaning user decline OAuth

    auth_code = request.args.get('code')
    username, refresh_token = get_username_refresh_token_from_code(auth_code)

    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username, refresh_token=refresh_token)
        DB.session.add(user)
        DB.session.commit()

    login_user(user, True)

    return redirect(url_for('index'))
