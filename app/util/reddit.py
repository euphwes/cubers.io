""" Utility functions for dealing with PRAW Reddit instances. """

from praw import Reddit

from app import app
from app.persistence.user_manager import get_user_by_username

# -------------------------------------------------------------------------------------------------

__REDIRECT         = app.config['REDDIT_REDIRECT_URI']
__CLIENT_ID        = app.config['REDDIT_CLIENT_ID']
__CLIENT_SECRET    = app.config['REDDIT_CLIENT_SECRET']
__APP_URL          = app.config['APP_URL']
__TARGET_SUBREDDIT = app.config['TARGET_SUBREDDIT']
__IS_DEVO          = app.config['IS_DEVO']
__USER_AGENT       = 'web:rcubersComps:v0.01 by /u/euphwes'

__PROD_CUBERSIO_ACCT = app.config['PROD_CUBERSIO_ACCT']
__DEVO_CUBERSIO_ACCT = app.config['DEVO_CUBERSIO_ACCT']

__APP_ACCT_OAUTH_SCOPES  = ['identity', 'read', 'submit', 'edit', 'privatemessages']
__USER_ACCT_OAUTH_SCOPES = ['identity']

__PERMANENT_LOGIN = 'permanent'

__REDDIT_URL_ROOT = 'http://www.reddit.com'

# -------------------------------------------------------------------------------------------------

def get_new_reddit():
    """ Returns a new, unauthenticated Reddit instance. """

    return Reddit(client_id=__CLIENT_ID, client_secret=__CLIENT_SECRET, redirect_uri=__REDIRECT,
                  user_agent=__USER_AGENT)


def get_non_user_reddit():
    """ Returns a PRAW instance for cases where we do not need to be authed as a user. """

    return Reddit(client_id=__CLIENT_ID, client_secret=__CLIENT_SECRET, redirect_uri=__REDIRECT,
                  user_agent=__USER_AGENT)


def get_authed_reddit_for_user(user):
    """ Returns a PRAW instance for this user using their refresh token. """

    return Reddit(client_id=__CLIENT_ID, client_secret=__CLIENT_SECRET,
                  refresh_token=user.reddit_token, user_agent=__USER_AGENT)


def get_authed_reddit_for_cubersio_acct():
    """ Returns a PRAW instance for the Reddit account to post the competition under. """

    if __IS_DEVO:
        token = get_user_by_username(__DEVO_CUBERSIO_ACCT).reddit_token
    else:
        token = get_user_by_username(__PROD_CUBERSIO_ACCT).reddit_token

    return Reddit(client_id=__CLIENT_ID, client_secret=__CLIENT_SECRET,
                  refresh_token=token, user_agent=__USER_AGENT)


def send_PM_to_user_with_title_and_body(username, title, body):
    """ Sends a Reddit PM with the specified message title and body to this user. """

    reddit = get_authed_reddit_for_cubersio_acct()
    reddit.redditor(username).message(title, body)


def get_permalink_for_thread_id(reddit_thread_id):
    """ Returns the permalink for the competition thread specified by the ID above. """

    try:
        comp = get_non_user_reddit().submission(id=reddit_thread_id)
        return __REDDIT_URL_ROOT + comp.permalink
        
    except Exception:
        return "Oops, no thread exists with that ID."


def submit_post(title, post_body):
    """ Submits a Reddit post, and returns a Reddit submission ID. """

    r = get_authed_reddit_for_cubersio_acct()
    cubers = r.subreddit(__TARGET_SUBREDDIT)

    return cubers.submit(title=title, selftext=post_body, send_replies=False).id


def update_post(post_body, thread_id):
    """ Updates a post with the given post_body. """

    r = get_authed_reddit_for_cubersio_acct()
    submission = r.submission(id=thread_id)
    submission.edit(post_body)

    return submission.id


def get_username_refresh_token_from_code(code):
    """ Returns the username and current refresh token for a given Reddit auth code. """

    reddit = get_new_reddit()
    refresh_token = reddit.auth.authorize(code)
    username = reddit.user.me().name

    return username, refresh_token


def get_reddit_auth_url(state):
    """ Returns a url for authentication with Reddit. """

    return get_new_reddit().auth.url(__USER_ACCT_OAUTH_SCOPES, state, __PERMANENT_LOGIN)


def get_app_account_auth_url(state='...'):
    """ Returns a url for authentication with Reddit.

    HACK ALERT: this is a special endpoint intended to be used just for cubers_io/cubers_io_test,
    to gain sufficient privileges to submit PMs from that account.
    
    TODO: figure out the right wayof doing this. """

    return get_new_reddit().auth.url(__APP_ACCT_OAUTH_SCOPES, state, __PERMANENT_LOGIN)
