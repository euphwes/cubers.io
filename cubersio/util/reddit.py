""" Utility functions for interacting with Reddit via PRAW (Python Reddit API Wrapper). """

from typing import Tuple

from praw import Reddit

from cubersio import app
from cubersio.persistence.user_manager import get_user_by_username


__REDIRECT_URI           = app.config['REDDIT_REDIRECT_URI']
__CLIENT_ID              = app.config['REDDIT_CLIENT_ID']
__CLIENT_SECRET          = app.config['REDDIT_CLIENT_SECRET']
__APP_URL                = app.config['APP_URL']
__TARGET_SUBREDDIT       = app.config['TARGET_SUBREDDIT']
__USER_AGENT             = 'web:cubers.io:v1.0 by /u/euphwes'
__APP_ACCT_OAUTH_SCOPES  = ['identity', 'read', 'submit', 'edit', 'privatemessages']
__USER_ACCT_OAUTH_SCOPES = ['identity']
__PERMANENT_LOGIN        = 'permanent'

if app.config['IS_DEVO']:
    __CUBERSIO_ACCT = app.config['DEVO_CUBERSIO_ACCT']
else:
    __CUBERSIO_ACCT = app.config['PROD_CUBERSIO_ACCT']


def __get_praw_instance() -> Reddit:
    """ Returns a new, unauthenticated PRAW instance. """

    return Reddit(client_id=__CLIENT_ID,
                  client_secret=__CLIENT_SECRET,
                  redirect_uri=__REDIRECT_URI,
                  user_agent=__USER_AGENT)


def __get_admin_praw_instance() -> Reddit:
    """ Returns a PRAW instance authed as the cubers.io internal Reddit account. """

    return Reddit(client_id=__CLIENT_ID,
                  client_secret=__CLIENT_SECRET,
                  refresh_token=get_user_by_username(__CUBERSIO_ACCT).reddit_token,
                  user_agent=__USER_AGENT)


def send_pm_to_user(username: str, title: str, body: str):
    """ Sends a Reddit PM with the specified message title and body to this user. """

    reddit = __get_admin_praw_instance()
    reddit.redditor(username).message(title, body)


def submit_post(title: str, post_body: str) -> str:
    """ Submits a Reddit post, and returns a Reddit submission ID. """

    cubers = __get_admin_praw_instance().subreddit(__TARGET_SUBREDDIT)
    return cubers.submit(title=title, selftext=post_body, send_replies=False).id


def update_post(post_body: str, thread_id: str) -> str:
    """ Updates a post with the given post_body. """

    r = __get_admin_praw_instance()
    submission = r.submission(id=thread_id)
    submission.edit(post_body)

    return submission.id


def get_username_and_refresh_token_from_code(code: str) -> Tuple[str, str]:
    """ Returns the username and current refresh token for a given Reddit auth code. """

    reddit = __get_praw_instance()
    refresh_token = reddit.auth.authorize(code)
    username = reddit.user.me().name

    return username, refresh_token


def get_reddit_auth_url(state: str) -> str:
    """ Returns a url for authentication with Reddit. """

    return __get_praw_instance().auth.url(__USER_ACCT_OAUTH_SCOPES, state, __PERMANENT_LOGIN)


def get_app_account_auth_url(state: str = '...') -> str:
    """ Returns a url for to authenticate an admin account with Reddit. This asks for more permissions than a regular
     username login, because we submit and edit results posts and send PMs from the admin account. """

    return __get_praw_instance().auth.url(__APP_ACCT_OAUTH_SCOPES, state, __PERMANENT_LOGIN)
