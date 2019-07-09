""" Contains all the config values for this web app. """

from os import environ
from os.path import abspath, dirname, join as path_join

# -------------------------------------------------------------------------------------------------

TEST_SUBREDDIT = 'cubecomps'

DEFAULT_PROD_ACCOUNT = 'cubers_io'
DEFAULT_DEVO_ACCOUNT = 'cubers_io_test'

# -------------------------------------------------------------------------------------------------

class Config(object):
    """ A config object whose attributes and their values get converted to key/value pairs
    in the web app's config dict. """

    FLASK_SECRET_KEY = environ.get('FLASK_SECRET_KEY')

    # ------------------------------------------------------
    # Reddit API config
    # ------------------------------------------------------
    REDDIT_CLIENT_ID     = environ.get('CUBERS_CLIENT_ID')
    REDDIT_CLIENT_SECRET = environ.get('CUBERS_SECRET')
    REDDIT_REDIRECT_URI  = environ.get('REDDIT_OAUTH_REDIRECT_URI')
    PROD_CUBERSIO_ACCT   = environ.get('PROD_CUBERSIO_ACCT', DEFAULT_PROD_ACCOUNT)
    DEVO_CUBERSIO_ACCT   = environ.get('DEVO_CUBERSIO_ACCT', DEFAULT_DEVO_ACCOUNT)

    # ------------------------------------------------------
    # Config related which subreddit to target, the URL to
    # the web app to drop into the Reddit comment body, etc
    # ------------------------------------------------------
    APP_URL          = environ.get('APP_URL', 'http://fake.url.com/')
    TARGET_SUBREDDIT = environ.get('TARGET_SUBREDDIT', TEST_SUBREDDIT)
    IS_DEVO          = TARGET_SUBREDDIT == TEST_SUBREDDIT

    # ------------------------------------------------------
    # Database config
    # ------------------------------------------------------
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Get the database URI. Assume there's a PostGRES DB connection URI in the env variables
    # If there isn't, fall back to just pointing at a sqlite database in the app root directory
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        basedir = abspath(dirname(__file__))
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path_join(basedir, 'cube_competitions.sqlite')

    # ------------------------------------------------------
    # Other config
    # ------------------------------------------------------
    TEMPLATES_AUTO_RELOAD = True

    # The factor by which we multiply current WRs to determine whether or not to automatically
    # blacklist results we are assuming to be fake
    AUTO_BL_FACTOR = float(environ.get('AUTO_BL_FACTOR', 1.0))
