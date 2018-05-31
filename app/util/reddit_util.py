""" Utility functions for dealing with PRAW Reddit instances. """

from praw import Reddit
from app import CUBERS_APP

REDIRECT      = CUBERS_APP.config['REDDIT_REDIRECT_URI']
USER_AGENT    = 'web:rcubersComps:v0.01 by /u/euphwes'
CLIENT_ID     = CUBERS_APP.config['REDDIT_CLIENT_ID']
CLIENT_SECRET = CUBERS_APP.config['REDDIT_CLIENT_SECRET']

# -------------------------------------------------------------------------------------------------

def get_new_reddit():
    """ Returns a new, unauthenticated Reddit instance. """
    return Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT,
                  user_agent = USER_AGENT)


#pylint: disable=C0103
def get_username_refresh_token_from_code(code):
    """ Returns the username and current refresh token for a given Reddit auth code. """
    reddit = get_new_reddit()
    refresh_token = reddit.auth.authorize(code)
    username = reddit.user.me().name

    return username, refresh_token


#pylint: disable=C0103
def get_user_auth_url(state='...'):
    """ Returns a url for authenticating with Reddit. """
    return get_new_reddit().auth.url(['identity', 'read', 'submit'], state, 'permanent')
