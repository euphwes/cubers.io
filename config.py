import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    REDDIT_CLIENT_ID     = os.environ.get('CUBERS_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.environ.get('CUBERS_SECRET')

    SQLALCHEMY_DATABASE_URI = os.environ.get('CUBERS_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False