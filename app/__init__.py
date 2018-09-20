""" Main initialization point of the web app. """

from os import environ

from flask import Flask
from flask_assets import Bundle, Environment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

# -------------------------------------------------------------------------------------------------

CUBERS_APP = Flask(__name__)
CUBERS_APP.config.from_object(Config)

CUBERS_APP.secret_key = CUBERS_APP.config['FLASK_SECRET_KEY']

DB = SQLAlchemy(CUBERS_APP)
MIGRATE = Migrate(CUBERS_APP, DB)

ASSETS = Environment(CUBERS_APP)
ASSETS.register({
    'app_js': Bundle(
        'js/event_emitter.js',
        'js/app.js',
        'js/convert_format_util.js',
        'js/init.js',
        filters="jsmin",
        output='gen/app.js'
    ),

    'app_css': Bundle(
        'less/cubers_common.less',
        filters="less,cssmin",
        output='gen/app.css'),
})

#pylint: disable=W0401
#I don't want to specifically name every route I want to import here
from app.persistence import models
from .routes import *
from .commands import create_new_test_comp
