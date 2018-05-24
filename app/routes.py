""" Defines some routes. """

from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_required, login_user, logout_user

from praw import Reddit

from app import CUBERS_APP, DB
from app.models import User

# -------------------------------------------------------------------------------------------------

REDDIT = Reddit(client_id = CUBERS_APP.config['REDDIT_CLIENT_ID'],
                client_secret = CUBERS_APP.config['REDDIT_CLIENT_SECRET'],
                redirect_uri = CUBERS_APP.config['REDDIT_REDIRECT_URI'], user_agent = 'test by /u/euphwes')

@CUBERS_APP.route('/')
@CUBERS_APP.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))

    return render_template('index.html')


@CUBERS_APP.route('/welcome')
@login_required
def welcome():
    users = User.query.all()
    return render_template('welcome.html', users=users)


@CUBERS_APP.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))

    #login_user(user, remember=form.remember_me.data)
    return redirect(REDDIT.auth.url(['identity', 'read', 'submit'], '...', 'permanent'))


@CUBERS_APP.route('/authorize')
def oauth_callback():
    """ """
    #state = request.args.get('state', '')
    code = request.args.get('code', '')

    if not REDDIT.user:
        return

    refresh_token = REDDIT.auth.authorize(code)

    username = REDDIT.user.me().name
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username, refresh_token=refresh_token)
        DB.session.add(user)
        DB.session.commit()

    login_user(user, True)

    return redirect(url_for('welcome'))


@CUBERS_APP.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))