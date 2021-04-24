""" Main initialization point of the web app. """

from flask import Flask, request
from flask.helpers import send_from_directory
from flask_assets import Bundle, Environment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mobility import Mobility

from config import Config

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


from cubersio.routes import *
from cubersio.util.template import *
from cubersio.commands import *
from queue_config import huey
