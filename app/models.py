from app import db, app
from datetime import datetime
from flask_login import LoginManager, UserMixin
from sqlalchemy.orm import relationship

# -------------------------------------------------------------------------------------------------

loginManager = LoginManager(app)

class User(UserMixin, db.Model):
    __tablename__  = 'users'
    id             = db.Column(db.Integer, primary_key=True)
    username       = db.Column(db.String(64), index=True, unique=True)
    wca_id         = db.Column(db.String(10))
    refresh_token  = db.Column(db.String(64))

@loginManager.user_loader
def load_user(id):
    return User.query.get(int(id))

# -------------------------------------------------------------------------------------------------

class Competition_Event(db.Model):
    """ Associative model for an event held at a competition - FKs to the competition and event,
    and a JSON array of scrambles. """
    __tablename__  = 'competition_event'
    id             = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'))
    event_id       = db.Column(db.Integer, db.ForeignKey('events.id'))
    scrambles      = db.Column(db.Text())


class Event(db.Model):
    """ A record for a specific cubing event -- the name of the puzzle, the total number of solves
    to be completed by a competitor, and an optional description of the event. """
    __tablename__  = 'events'
    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(64), index=True, unique=True)
    totalSolves    = db.Column(db.Integer)
    description    = db.Column(db.String(128))


class Competition(db.Model):
    """ A record for a competition -- the title of the competition, the start and end datetime,
    the list of events held in the competition, and a JSON field containing total user points results."""
    __tablename__    = 'competitions'
    id               = db.Column(db.Integer, primary_key=True)
    title            = db.Column(db.String(128), index=True, unique=True)
    start_timestamp  = db.Column(db.DateTime)
    end_timestamp    = db.Column(db.DateTime)
    userPointResults = db.Column(db.Text())
    events           = relationship('Competition_Event', backref='event', primaryjoin=id == Competition_Event.competition_id)


class UserEventResults(db.Model):
    """ stuff """
    __tablename__ = 'user_event_results'
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'))
    comp_event_id = db.Column(db.Integer, db.ForeignKey('competition_event.id'))
    single        = db.Column(db.Integer)
    average       = db.Column(db.Integer)
    solve1        = db.Column(db.Integer)
    solve2        = db.Column(db.Integer)
    solve3        = db.Column(db.Integer)
    solve4        = db.Column(db.Integer)
    solve5        = db.Column(db.Integer)
