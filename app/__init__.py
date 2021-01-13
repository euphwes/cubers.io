""" Main initialization point of the web app. """

from urllib.parse import urlencode

from flask import Flask
from flask.helpers import send_from_directory
from flask_assets import Bundle, Environment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mobility import Mobility

from babel.dates import format_date

from slugify import slugify

from config import Config

from app.util.events import build_mbld_results

# -------------------------------------------------------------------------------------------------

app = Flask(__name__)
app.config.from_object(Config)

Mobility(app)

app.secret_key = app.config['FLASK_SECRET_KEY']

DB = SQLAlchemy(app)
MIGRATE = Migrate(app, DB)

ASSETS = Environment(app)
ASSETS.register({

    # --------- common static bundles ------------

    'init_js': Bundle(
        'js/init.js',
        filters="jsmin",
        output='gen/init.js'
    ),

    # --------- home page static bundles ------------

    'index_js': Bundle(
        'js/home/home_page.js',
        'js/ui/shapes.js',
        filters="jsmin",
        output='gen/index.js'
    ),

    'shapes_js': Bundle(
        'js/ui/shapes.js',
        filters="jsmin",
        output='gen/shapes.js'
    ),

    'index_css': Bundle(
        'less/common.less',
        'less/navbar.less',
        'less/events_page.less',
        'less/home/common.less',
        filters="less,cssmin",
        output='gen/index.css'),

    # --------- timer page static bundles ------------

    'timer_timer_js': Bundle(
        'js/event_emitter.js',
        'js/controller/user_settings_manager.js',
        'js/util/extensions_and_polyfill.js',
        'js/util/time_convert_format.js',
        'js/ui/scramble_image_generator.js',
        'js/ui/shapes.js',
        'js/timer/timer_common.js',
        'js/timer/timer_controller.js',
        'js/timer/timer_display_manager.js',
        'js/timer/timer_page.js',
        'js/timer/timer_control_buttons.js',
        filters="jsmin",
        output='gen/timer_timer.js'
    ),

    'timer_manual_js': Bundle(
        'js/event_emitter.js',
        'js/controller/user_settings_manager.js',
        'js/util/extensions_and_polyfill.js',
        'js/util/time_convert_format.js',
        'js/ui/scramble_image_generator.js',
        'js/ui/shapes.js',
        'js/timer/timer_common.js',
        'js/timer/timer_manual.js',
        'js/timer/timer_control_buttons.js',
        filters="jsmin",
        output='gen/timer_manual.js'
    ),

    'timer_fmc_js': Bundle(
        'js/event_emitter.js',
        'js/controller/user_settings_manager.js',
        'js/util/extensions_and_polyfill.js',
        'js/util/time_convert_format.js',
        'js/ui/scramble_image_generator.js',
        'js/ui/shapes.js',
        'js/timer/timer_common.js',
        'js/timer/timer_fmc.js',
        'js/timer/timer_control_buttons.js',
        filters="jsmin",
        output='gen/timer_fmc.js'
    ),

    'timer_mbld_js': Bundle(
        'js/event_emitter.js',
        'js/controller/user_settings_manager.js',
        'js/util/extensions_and_polyfill.js',
        'js/util/time_convert_format.js',
        'js/ui/scramble_image_generator.js',
        'js/ui/shapes.js',
        'js/timer/timer_common.js',
        'js/timer/timer_mbld.js',
        'js/timer/timer_control_buttons.js',
        filters="jsmin",
        output='gen/timer_mbld.js'
    ),

    'timer_desktop_css': Bundle(
        'less/common.less',
        'less/navbar.less',
        'less/timer/common.less',
        'less/timer/desktop.less',
        filters="less,cssmin",
        output='gen/timer_desktop.css'),

    'timer_mobile_css': Bundle(
        'less/common.less',
        'less/navbar.less',
        'less/timer/common.less',
        'less/timer/mobile.less',
        filters="less,cssmin",
        output='gen/timer_mobile.css'),

    # --------- user settings page static bundles ------------

    'user_settings_js': Bundle(
        'js/controller/user_settings_manager.js',
        'js/ui/scramble_image_generator.js',
        filters="jsmin",
        output='gen/user_settings.js'),

    'user_settings_css': Bundle(
        'less/common.less',
        'less/navbar.less',
        'less/timer/common.less',
        'less/timer/desktop.less',
        'less/timer/mobile.less',
        'less/events_page.less',
        'less/results.less',
        'less/user.less',
        'less/event_results.less',
        'less/settings.less',
        'less/home/common.less',
        'css/bootstrap-social.min.css',
        filters="less,cssmin",
        output='gen/user_settings.css'),

    # --------- the rest ------------

    'app_css': Bundle(
        'less/common.less',
        'less/navbar.less',
        'less/timer/common.less',
        'less/timer/desktop.less',
        'less/timer/mobile.less',
        'less/events_page.less',
        'less/results.less',
        'less/user.less',
        'less/event_results.less',
        'less/settings.less',
        'css/bootstrap-social.min.css',
        filters="less,cssmin",
        output='gen/app.css'),
})


@app.route('/robots.txt')
def static_from_root():
    return send_from_directory('static', request.path[1:])

# -------------------------------------------------------------------------------------------------

from app.tasks import *

from app.persistence import models
from app.routes.admin import *
from app.routes.auth import *
from app.routes.events import *
from app.routes.home import *
from app.routes.persistence import *
from app.routes.results import *
from app.routes.user import *
from app.routes.util import *
from app.commands import *
from app.util.times import convert_centiseconds_to_friendly_time

# -------------------------------------------------------------------------------------------------

@app.context_processor
def link_to_algcubingnet():
    """ Generates an anchor with a link to alg.cubing.net for the specified set and algorithm/moves. """

    def __link_to_algcubingnet(setup, alg, moves_count):
        """ Generates an anchor with a link to alg.cubing.net for the specified set and algorithm/moves. """

        # If no solution was provided, the solve probably predated the required FMC solutions feature
        # Don't render a link to alg.cubing.net; instead just render the moves count
        if not alg:
            return moves_count

        anchor = '<a href="https://alg.cubing.net/?{}" style="font-size: 14px;" target="_blank">{} <i class="fas fa-external-link-alt"></i></a>'
        querystring = urlencode([
            ('setup', setup),
            ('alg', alg),
            ('type', 'reconstruction'),
        ])

        return anchor.format(querystring, moves_count)

    return dict(link_to_algcubingnet=__link_to_algcubingnet)


@app.template_filter('slugify')
def slugify_filter(value):
    """ Jinja custom filter to slugify a string. """

    return slugify(value)


@app.template_filter('format_datetime')
def format_datetime(value):
    """ Jinja custom filter to format a date to Apr 1, 2018 format. """

    return format_date(value, locale='en_US')


@app.template_filter('friendly_time')
def friendly_time(value):
    """ Jinja custom filter to convert a time in cs to a user-friendly time. """

    if value is None:
        return ''

    try:
        converted_value = int(value)
    except ValueError:
        return value
    return convert_centiseconds_to_friendly_time(converted_value)


@app.template_filter('format_fmc_result')
def format_fmc_result(value):
    """ Jinja custom filter to convert a fake 'centisecond' result to FMC moves. """

    if value is None:
        return ''

    try:
        converted_value = int(value) / 100
    except ValueError:
        return value

    if converted_value == int(converted_value):
        converted_value = int(converted_value)

    return converted_value


@app.template_filter('format_mbld_result')
def format_mbld_result(value):
    """ Jinja custom filter to convert a fake 'centisecond' result to MBLD results. """

    if value is None:
        return ''

    if not value:
        return ''

    return build_mbld_results(value)
