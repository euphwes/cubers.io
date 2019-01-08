""" Main initialization point of the web app. """

from os import environ

from flask import Flask
from flask_assets import Bundle, Environment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from babel.dates import format_date
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

        'js/util/time_convert_format.js',
        'js/util/extensions_and_polyfill.js',
        'js/util/handlebars_helpers.js',

        'js/controller/app_mode_manager.js',

        'js/timer.js',

        'js/controller/events_data_manager.js',
        'js/controller/current_scrambles_manager.js',

        'js/ui/solve_card_manager.js',
        'js/ui/timer_display_manager.js',
        'js/ui/scramble_display_manager.js',
        'js/ui/main_screen_manager.js',
        'js/ui/timer_screen_manager.js',
        'js/ui/summary_screen_manager.js',
        'js/ui/scramble_image_generator.js',

        'js/init.js',
        filters="jsmin",
        output='gen/app.js'
    ),

    'app_css': Bundle(
        'less/common.less',
        'less/navbar.less',
        'less/timer_page.less',
        'less/events_page.less',
        'less/summary.less',
        'less/results.less',
        'less/user.less',
        'less/event_results.less',
        filters="less,cssmin",
        output='gen/app.css'),
})

# -------------------------------------------------------------------------------------------------

# pylint: disable=W0401
# I don't want to specifically name every route I want to import here
from app.persistence import models
from .routes import *
from .commands import *
from .util.times_util import convert_centiseconds_to_friendly_time

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.template_filter('format_datetime')
def format_datetime(value):
    """ Jinja custom filter to format a date to Apr 1, 2018 format. """

    return format_date(value, locale='en_US')


@CUBERS_APP.template_filter('friendly_time')
def friendly_time(value):
    """ Jinja custom filter to convert a time in cs to a user-friendly time. """

    try:
        converted_value = int(value)
    except ValueError:
        return value
    return convert_centiseconds_to_friendly_time(converted_value)


@CUBERS_APP.template_filter('format_fmc_result')
def format_fmc_result(value):
    """ Jinja custom filter to convert a fake 'centisecond' result to FMC moves. """

    try:
        converted_value = int(value)/100
    except ValueError:
        return value

    if converted_value == int(converted_value):
        converted_value = int(converted_value)

    return converted_value
