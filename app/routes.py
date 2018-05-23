from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_user

from app import app, db

from app.models import User
from praw import Reddit

# -------------------------------------------------------------------------------------------------
reddit = Reddit(client_id = app.config['REDDIT_CLIENT_ID'], client_secret = app.config['REDDIT_CLIENT_SECRET'],
                redirect_uri = 'http://localhost:5000/oauth', user_agent = 'test by /u/euphwes')

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    #login_user(user, remember=form.remember_me.data)
    return redirect(reddit.auth.url(['identity', 'read', 'submit'], '...', 'permanent'))


@app.route('/oauth')
def oauth_callback():
    state = request.args.get('state','')
    code = request.args.get('code','')

    if not reddit.user:
        return

    refresh_token = reddit.auth.authorize(code)

    username = reddit.user.name
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username)
        db.session.add(user)
        db.session.commit()

    login_user(user, True)

    return redirect(url_for('index'))