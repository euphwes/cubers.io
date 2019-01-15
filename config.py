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

    REDDIT_CLIENT_ID        = environ.get('CUBERS_CLIENT_ID')
    REDDIT_CLIENT_SECRET    = environ.get('CUBERS_SECRET')
    REDDIT_REDIRECT_URI     = environ.get('REDDIT_OAUTH_REDIRECT_URI')
    FLASK_SECRET_KEY        = environ.get('FLASK_SECRET_KEY')
    SCRIPT_API_KEY          = environ.get('SCRIPT_API_KEY')
    APP_URL                 = environ.get('APP_URL', 'http://fake.url.com')
    TARGET_SUBREDDIT        = environ.get('TARGET_SUBREDDIT', TEST_SUBREDDIT)
    IS_DEVO                 = TARGET_SUBREDDIT == TEST_SUBREDDIT

    AUTO_BL_FACTOR          = float(environ.get('AUTO_BL_FACTOR', 1.0))

    PROD_CUBERSIO_ACCT      = environ.get('PROD_CUBERSIO_ACCT', DEFAULT_PROD_ACCOUNT)
    DEVO_CUBERSIO_ACCT      = environ.get('DEVO_CUBERSIO_ACCT', DEFAULT_DEVO_ACCOUNT)

    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        basedir = abspath(dirname(__file__))
        SQLALCHEMY_DATABASE_URI =  'sqlite:///' + path_join(basedir, 'cube_competitions.sqlite')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True
