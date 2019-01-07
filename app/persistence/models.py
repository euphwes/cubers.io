""" SQLAlchemy models for all database entries. """

from collections import OrderedDict
import json

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
    """ Competition event formats: Average of 5, Mean of 3, Best of 3, Best of 1. """
    Ao5 = "Ao5"
    Mo3 = "Mo3"
    Bo3 = "Bo3"
    Bo1 = "Bo1"

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
    is_admin       = Column(Boolean)
    results        = relationship("UserEventResults", backref="User")

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
    eventFormat    = Column(Enum("Ao5", "Mo3", "Bo3", "Bo1", name="eventFormat"), default="Ao5")
    description    = Column(String(128))
    CompEvents     = relationship("CompetitionEvent", backref="Event")


class Scramble(Model):
    """ A scramble for a specific event at a specific competition. """
    __tablename__        = 'scrambles'
    id                   = Column(Integer, primary_key=True)
    scramble             = Column(Text())
    competition_event_id = Column(Integer, ForeignKey('competition_event.id'))
    solves               = relationship('UserSolve', backref='Scramble')

    def to_front_end_consolidated_dict(self):
        """ Returns a dictionary representation of this object, for use in the front-end.
        Adds a few additional fields so that the front-end object can be easily translated
        to a UserSolve object when sent back to the backend. """

        return {
            'id':        self.id,
            'scramble':  self.scramble,
            'time':      0,
            'isPlusTwo': False,
            'isDNF':     False,
        }


class UserEventResults(Model):
    """ A model detailing a user's results for a single event at competition. References the user,
    the competitionEvent, the single and average result for the event. These values are either in
    centiseconds (ex: "1234" = 12.34s), units for FMC (ex: "28" = 28 moves) or "DNF". """
    __tablename__     = 'user_event_results'
    id                = Column(Integer, primary_key=True)
    user_id           = Column(Integer, ForeignKey('users.id'))
    comp_event_id     = Column(Integer, ForeignKey('competition_event.id'), index=True)
    single            = Column(String(10))
    average           = Column(String(10))
    result            = Column(String(10))
    comment           = Column(Text)
    solves            = relationship('UserSolve')
    reddit_comment    = Column(String(10))
    is_complete       = Column(Boolean)
    times_string      = Column(Text)
    was_pb_single     = Column(Boolean)
    was_pb_average    = Column(Boolean)
    is_blacklisted    = Column(Boolean)
    blacklist_note    = Column(String(256))


class CompetitionEvent(Model):
    """ Associative model for an event held at a competition - FKs to the competition and event,
    and a JSON array of scrambles. """
    __tablename__  = 'competition_event'
    id             = Column(Integer, primary_key=True)
    competition_id = Column(Integer, ForeignKey('competitions.id'), index=True)
    event_id       = Column(Integer, ForeignKey('events.id'), index=True)
    scrambles      = relationship('Scramble', backref='CompetitionEvent',
                                  primaryjoin = id == Scramble.competition_event_id)
    user_results   = relationship('UserEventResults', backref='CompetitionEvent',
                                  primaryjoin = id == UserEventResults.comp_event_id)

    def to_front_end_consolidated_dict(self):
        """ Returns a dictionary representation of this object for use in the front-end.
        Adds a few additional fields so that the front-end object can be easily translated
        to a UserEventResults object when sent back to the backend. """

        return {
            'name':          self.Event.name,
            'scrambles':     [s.to_front_end_consolidated_dict() for s in self.scrambles],
            'event_id':      self.Event.id,
            'comp_event_id': self.id,
            'event_format':  self.Event.eventFormat,
            'comment':       '',
        }


class Competition(Model):
    """ A record for a competition -- the title of the competition, the start and end datetime,
    the list of events held, and a JSON field containing total user points results."""
    __tablename__    = 'competitions'
    id               = Column(Integer, primary_key=True)
    title            = Column(String(128))
    reddit_thread_id = Column(String(10), index=True, unique=True)
    result_thread_id = Column(String(10), index=True)
    start_timestamp  = Column(DateTime(timezone=True))
    end_timestamp    = Column(DateTime(timezone=True))
    active           = Column(Boolean)
    events           = relationship('CompetitionEvent', backref='Competition',
                                    primaryjoin=id == CompetitionEvent.competition_id)


class CompetitionGenResources(Model):
    """ A record for maintaining the current state of the competition generation. """
    __tablename__       = 'comp_gen_resources'
    id                  = Column(Integer, primary_key=True)
    current_comp_id     = Column(Integer)
    previous_comp_id    = Column(Integer)
    current_comp_num    = Column(Integer)
    current_bonus_index = Column(Integer)
    current_OLL_index   = Column(Integer)


class UserSiteRankings(Model):
    """ A record for holding pre-calculated user PB single and averages, and site rankings,
    for each event they have participated in. """
    __tablename__  = 'user_site_rankings'
    id          = Column(Integer, primary_key=True)
    user_id     = Column(Integer, ForeignKey('users.id'), index=True)
    user        = relationship('User', primaryjoin = user_id == User.id)
    comp_id     = Column(Integer, ForeignKey('competitions.id'))
    competition = relationship('Competition', primaryjoin = comp_id == Competition.id)
    data        = Column(String(2048))

    def get_site_rankings_data_as_dict(self):
        """ Deserializes data field to json to return site rankings info as a dict. """

        # The keys (event ID) get converted to strings when serializing to json.
        # We need them as ints, so iterate through the deserialized dict, building a new
        # one with ints as keys instead of strings. Return that.
        site_rankings = OrderedDict()
        for key, value in json.loads(self.data, object_pairs_hook=OrderedDict).items():
            site_rankings[int(key)] = value

        return site_rankings


class UserSolve(Model):
    """ A user's solve for a specific scramble, in a specific event, at a competition.
    Solve times are in centiseconds (ex: 1234 = 12.34s)."""

    __tablename__ = 'user_solves'
    id            = Column(Integer, primary_key=True)
    time          = Column(Integer)
    is_dnf        = Column(Boolean, default=False)
    is_plus_two   = Column(Boolean, default=False)
    scramble_id   = Column(Integer, ForeignKey('scrambles.id'))
    user_event_results_id = Column(Integer, ForeignKey('user_event_results.id'))

    def get_total_time(self):
        """ Returns the solve's time with +2s penalty counted, if applicable. """
        return (self.time + 200) if self.is_plus_two else self.time
