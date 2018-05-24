from os import environ

class Config(object):
    REDDIT_CLIENT_ID     = environ.get('CUBERS_CLIENT_ID')
    REDDIT_CLIENT_SECRET = environ.get('CUBERS_SECRET')
    REDDIT_REDIRECT_URI  = environ.get('REDDIT_OAUTH_REDIRECT_URI')
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False