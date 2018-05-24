""" Defines some routes. """

from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_required, login_user, logout_user

from praw import Reddit

from app import app, db
from app.models import User

# -------------------------------------------------------------------------------------------------

reddit = Reddit(client_id = app.config['REDDIT_CLIENT_ID'], client_secret = app.config['REDDIT_CLIENT_SECRET'],
                redirect_uri = app.config['REDDIT_REDIRECT_URI'], user_agent = 'test by /u/euphwes')

@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))

    return render_template('index.html')


@app.route('/welcome')
@login_required
def welcome():
    users = User.query.all()
    return render_template('welcome.html', users=users)


@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))

    #login_user(user, remember=form.remember_me.data)
    return redirect(reddit.auth.url(['identity', 'read', 'submit'], '...', 'permanent'))


@app.route('/authorize')
def oauth_callback():
    """ """
    #state = request.args.get('state', '')
    code = request.args.get('code', '')

    if not reddit.user:
        return

    refresh_token = reddit.auth.authorize(code)

    username = reddit.user.me().name
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username, refresh_token=refresh_token)
        db.session.add(user)
        db.session.commit()

    login_user(user, True)

    return redirect(url_for('welcome'))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))