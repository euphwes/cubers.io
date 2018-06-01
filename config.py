""" Contains all the config values for this web app. """

from os import environ

class Config(object):
    """ A config object whose attributes and their values get converted to key/value pairs
    in the web app's config dict. """
    REDDIT_CLIENT_ID     = environ.get('CUBERS_CLIENT_ID')
    REDDIT_CLIENT_SECRET = environ.get('CUBERS_SECRET')
    REDDIT_REDIRECT_URI  = environ.get('REDDIT_OAUTH_REDIRECT_URI')
    FLASK_SECRET_KEY     = environ.get('FLASK_SECRET_KEY')
    SCRIPT_API_KEY       = environ.get('SCRIPT_API_KEY')

    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
