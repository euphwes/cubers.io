from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from os import environ

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = environ.get('FLASK_SECRET_KEY')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models