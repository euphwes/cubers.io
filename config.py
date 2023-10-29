""" Contains all the config values for this web app. """
# pylint: disable=line-too-long

from os import environ
from os.path import abspath, dirname, join as path_join

# -------------------------------------------------------------------------------------------------

TEST_SUBREDDIT = 'cubecomps'

DEFAULT_PROD_ACCOUNT = 'cubers_io'
DEFAULT_DEVO_ACCOUNT = 'cubers_io_test'

DEFAULT_ADMIN_REDDIT_USER = 'euphwes'

DEFAULT_CODE_TOP_OFF_THRESHOLD = 3

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
    # WCA OAuth config
    # ------------------------------------------------------
    WCA_CLIENT_ID     = environ.get('WCA_CLIENT_ID')
    WCA_CLIENT_SECRET = environ.get('WCA_SECRET')
    WCA_REDIRECT_URI  = environ.get('WCA_OAUTH_REDIRECT_URI')

    # ------------------------------------------------------
    # Config related to weekly SCS gift code recipient admin
    # ------------------------------------------------------
    CODE_CONFIRM_REDDIT_USER = environ.get('CODE_CONFIRM_REDDIT_USER', DEFAULT_ADMIN_REDDIT_USER)
    CODE_TOP_OFF_REDDIT_USER = environ.get('CODE_TOP_OFF_REDDIT_USER', DEFAULT_ADMIN_REDDIT_USER)

    try:
        CODE_TOP_OFF_THRESHOLD = int(environ.get('CODE_TOP_OFF_THRESHOLD', DEFAULT_CODE_TOP_OFF_THRESHOLD))
    except ValueError:
        CODE_TOP_OFF_THRESHOLD = DEFAULT_CODE_TOP_OFF_THRESHOLD


    # ------------------------------------------------------
    # Config related to notifying an admin of task status
    # ------------------------------------------------------
    TASK_STATUS_REDDIT_USER = environ.get('TASK_STATUS_REDDIT_USER', DEFAULT_ADMIN_REDDIT_USER)

    # ------------------------------------------------------
    # Config related which subreddit to target, the URL to
    # the web app to drop into the Reddit comment body, etc
    # ------------------------------------------------------
    APP_URL          = environ.get('APP_URL', 'http://localhost:5000/')
    TARGET_SUBREDDIT = environ.get('TARGET_SUBREDDIT', TEST_SUBREDDIT)
    IS_DEVO          = TARGET_SUBREDDIT == TEST_SUBREDDIT

    # ------------------------------------------------------
    # Database config
    # ------------------------------------------------------
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Get the database URI. Assume there's a PostGRES DB connection URI in the env variables
    # If there isn't, fall back to just pointing at a sqlite database in the app root directory
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
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
