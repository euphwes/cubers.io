from flask import Flask
from flask_assets import Bundle, Environment
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

from os import environ

bundles = {
    'main_js': Bundle(
        'js/cubers_common.js',
        filters="jsmin",
        output='gen/main.js'),

    'main_css': Bundle(
        'css/cubers_common.less',
        filters="less,yui_css",
        output='gen/main.css'),
}

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = environ.get('FLASK_SECRET_KEY')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

Bootstrap(app)

assets = Environment(app)
assets.register(bundles)

from app import routes, models
