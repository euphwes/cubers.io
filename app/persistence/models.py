""" SQLAlchemy models for all database entries. """

from flask_login import LoginManager, UserMixin
from sqlalchemy.orm import relationship

from app import DB, CUBERS_APP

#pylint: disable=C0103
Text       = DB.Text
Enum       = DB.Enum
Model      = DB.Model
Column     = DB.Column
String     = DB.String
Boolean    = DB.Boolean
Integer    = DB.Integer
DateTime   = DB.DateTime
ForeignKey = DB.ForeignKey

#pylint: disable=R0903
class EventFormat():
    """ Competition event formats: Average of 5, Mean of 3, or Best of 3. """
    Ao5 = "Ao5"
    Mo3 = "Mo3"
    Bo3 = "Bo3"

# -------------------------------------------------------------------------------------------------

class User(UserMixin, Model):
    """ A simple model of a user. We know these will only be created either through OAuth-ing with
    Reddit, or by uploading solve records via API call, so all we really need is a username and
    a Reddit refresh token. WCA ID is optional for user profiles. """
    __tablename__  = 'users'
    id             = Column(Integer, primary_key=True)
    username       = Column(String(64), index=True, unique=True)
    wca_id         = Column(String(10))
    refresh_token  = Column(String(64))

LOGIN_MANAGER = LoginManager(CUBERS_APP)
@LOGIN_MANAGER.user_loader
def load_user(user_id):
    """ Required by Flask-Login for loading a user by PK. """
    return User.query.get(int(user_id))

# -------------------------------------------------------------------------------------------------

class Event(Model):
    """ A record for a specific cubing event -- the name of the puzzle, the total number of solves
    to be completed by a competitor, and an optional description of the event. """
    __tablename__  = 'events'
    id             = Column(Integer, primary_key=True)
    name           = Column(String(64), index=True, unique=True)
    totalSolves    = Column(Integer)
    eventFormat    = Column(Enum("Ao5", "Mo3", "Bo3", name="eventFormat"), default="Ao5")
    description    = Column(String(128))
    CompEvents = relationship("CompetitionEvent", backref="Event")

class CompetitionEvent(Model):
    """ Associative model for an event held at a competition - FKs to the competition and event,
    and a JSON array of scrambles. """
    __tablename__  = 'competition_event'
    id             = Column(Integer, primary_key=True)
    competition_id = Column(Integer, ForeignKey('competitions.id'))
    event_id       = Column(Integer, ForeignKey('events.id'))
    scrambles      = Column(Text())


class Competition(Model):
    """ A record for a competition -- the title of the competition, the start and end datetime,
    the list of events held, and a JSON field containing total user points results."""
    __tablename__    = 'competitions'
    id               = Column(Integer, primary_key=True)
    title            = Column(String(128), index=True, unique=True)
    reddit_thread_id = Column(String(10), index=True, unique=True)
    start_timestamp  = Column(DateTime(timezone=True))
    end_timestamp    = Column(DateTime(timezone=True))
    active           = Column(Boolean)
    userPointResults = Column(Text())
    events           = relationship('CompetitionEvent', backref='Competition',
                                    primaryjoin=id == CompetitionEvent.competition_id)


class UserEventResults(Model):
    """ A model detail a user's results for a single event at competition. References the user,
    the competitionEvent, and has fields for best single, average, and up to five solves.
    Solve times are in centiseconds (ex: 1234 = 12.34s). """
    __tablename__ = 'user_event_results'
    id            = Column(Integer, primary_key=True)
    user_id       = Column(Integer, ForeignKey('users.id'))
    comp_event_id = Column(Integer, ForeignKey('competition_event.id'))
    single        = Column(Integer)
    average       = Column(Integer)
    solve1        = Column(Integer)
    solve2        = Column(Integer)
    solve3        = Column(Integer)
    solve4        = Column(Integer)
    solve5        = Column(Integer)
