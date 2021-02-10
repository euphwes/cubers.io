""" SQLAlchemy models for all database entries. """

from collections import namedtuple
import json

from flask_login import LoginManager, UserMixin, AnonymousUserMixin
from sqlalchemy.orm import relationship, reconstructor

from cubersio import DB, app
from cubersio.util.times import convert_centiseconds_to_friendly_time
from cubersio.util.events.mbld import MbldSolve

Text       = DB.Text
Enum       = DB.Enum
Model      = DB.Model
Column     = DB.Column
String     = DB.String
Float      = DB.Float
Boolean    = DB.Boolean
Integer    = DB.Integer
DateTime   = DB.DateTime
ForeignKey = DB.ForeignKey

class EventFormat():
    """ Competition event formats: Average of 5, Mean of 3, Best of 3, Best of 1. """
    Ao5 = "Ao5"
    Mo3 = "Mo3"
    Bo3 = "Bo3"
    Bo1 = "Bo1"

# Container for sum of ranks data
SumOfRanks = namedtuple('SumOfRanks', ['username', 'single', 'average'])
Kinchranks = namedtuple('KinchRanks', ['username', 'value', 'display'])

# -------------------------------------------------------------------------------------------------

class User(UserMixin, Model):
    """ A simple model of a user, which can be associated with one or both of Reddit and WCA.
    Username is populated with either WCA ID or Reddit username at first login, when the account is
    created. """
    __tablename__    = 'users'
    id               = Column(Integer, primary_key=True)
    username         = Column(String(64), index=True, unique=True)
    reddit_id        = Column(String(64))
    reddit_token     = Column(String(64))
    wca_id           = Column(String(10))
    wca_token        = Column(String(64))
    is_admin         = Column(Boolean)
    is_verified      = Column(Boolean)
    always_blacklist = Column(Boolean)
    results          = relationship("UserEventResults", backref="User")


class Nobody(AnonymousUserMixin):
    """ Utility class for an anonymous user. Subclasses Flask-Login AnonymousUserMixin to provide the
    default behavior given to non-logged-in users, but also evaluates to false in a boolean context,
    has a default username attribute and False `is_admin`, so that `current_user` can always be used
    for logging and checking permissions directly. """

    def __init__(self, username=None):
        self.username = username if username else '<no_user>'
        self.is_admin = False

    def __bool__(self):
        return False


LOGIN_MANAGER = LoginManager(app)
@LOGIN_MANAGER.user_loader
def load_user(user_id):
    """ Required by Flask-Login for loading a user by PK. """

    return User.query.get(int(user_id))


# Return a "Nobody" instance as the anonymous user here for Flask-Login
LOGIN_MANAGER.anonymous_user = lambda: Nobody()

# -------------------------------------------------------------------------------------------------

class Event(Model):
    """ A record for a specific cubing event -- the name of the puzzle, the total number of solves
    to be completed by a competitor, and an optional description of the event. """

    __tablename__  = 'events'
    id             = Column(Integer, primary_key=True)
    name           = Column(String(64), index=True, unique=True)
    totalSolves    = Column(Integer)
    description    = Column(String(2048))
    eventFormat    = Column(Enum("Ao5", "Mo3", "Bo3", "Bo1", name="eventFormat"), default="Ao5")
    CompEvents     = relationship("CompetitionEvent", backref="Event")


class ScramblePool(Model):
    """ A record that encapsulates a pre-generated scramble for a given event. """

    __tablename__ = 'scramble_pool'
    id            = Column(Integer, primary_key=True)
    event_id      = Column(Integer, ForeignKey('events.id'))
    scramble      = Column(Text())
    event         = relationship("Event", backref="scramble_pool")


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
    centiseconds (ex: "1234" = 12.34s), 10x units for FMC (ex: "2833" = 28.33 moves) or "DNF". """

    __tablename__     = 'user_event_results'
    id                = Column(Integer, primary_key=True)
    user_id           = Column(Integer, ForeignKey('users.id'))
    comp_event_id     = Column(Integer, ForeignKey('competition_event.id'), index=True)
    single            = Column(String(10))
    average           = Column(String(10))
    result            = Column(String(10))
    comment           = Column(Text)
    solves            = relationship('UserSolve', order_by=lambda: UserSolve.scramble_id)
    reddit_comment    = Column(String(10))
    is_complete       = Column(Boolean)
    times_string      = Column(Text)
    was_pb_single     = Column(Boolean)
    was_pb_average    = Column(Boolean)
    is_blacklisted    = Column(Boolean)
    blacklist_note    = Column(String(256))
    was_gold_medal    = Column(Boolean)
    was_silver_medal  = Column(Boolean)
    was_bronze_medal  = Column(Boolean)

    @reconstructor
    def init_on_load(self):
        """ Determine on load if these results are for FMC, or for a blind event, to facilitate
        getting user-friendly representations of individual solve times and overall result, single
        or average. """

        event_name = self.CompetitionEvent.Event.name
        self.is_fmc   = event_name == 'FMC'
        self.is_blind = event_name in ('2BLD', '3BLD', '4BLD', '5BLD')
        self.is_mbld  = event_name == 'MBLD'


    def set_solves(self, incoming_solves):
        """ Utility method to set a list of UserSolves for this UserEventResults. """

        self.solves.extend(incoming_solves)


    def friendly_result(self):
        """ Get a user-friendly representation of this UserEventResults's result field. """

        return self.__format_for_friendly(self.result)


    def friendly_single(self):
        """ Get a user-friendly representation of this UserEventResults's single field. """

        return self.__format_for_friendly(self.single)


    def friendly_average(self):
        """ Get a user-friendly representation of this UserEventResults's average field. """

        return self.__format_for_friendly(self.average)


    def __format_for_friendly(self, value):
        """ Utility method to return a friendly representation of the value passed in. Depends
        on whether or not this UserEventResults is for an FMC event or not. """

        if not value:
            return ''

        if value == 'DNF':
            return value

        if self.is_fmc:
            converted_value = int(value) / 100
            if converted_value == int(converted_value):
                converted_value = int(converted_value)
            return converted_value

        if self.is_mbld:
            return str(MbldSolve(value))

        return convert_centiseconds_to_friendly_time(value)


class CompetitionEvent(Model):
    """ Associative model for an event held at a competition - FKs to the competition and event,
    and a JSON array of scrambles. """

    __tablename__  = 'competition_event'
    id             = Column(Integer, primary_key=True)
    competition_id = Column(Integer, ForeignKey('competitions.id'), index=True)
    event_id       = Column(Integer, ForeignKey('events.id'), index=True)
    scrambles      = relationship('Scramble', backref='CompetitionEvent',
                                  primaryjoin=id == Scramble.competition_event_id, order_by=lambda: Scramble.id)
    user_results   = relationship('UserEventResults', backref='CompetitionEvent',
                                  primaryjoin=id == UserEventResults.comp_event_id)

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
    all_events          = Column(Boolean)
    title_override      = Column(String(128))


class UserSiteRankings(Model):
    """ A record for holding pre-calculated user PB single and averages, and site rankings,
    for each event they have participated in."""

    __tablename__  = 'user_site_rankings'
    id                  = Column(Integer, primary_key=True)
    user_id             = Column(Integer, ForeignKey('users.id'), index=True)
    user                = relationship('User', primaryjoin=user_id == User.id)
    data                = Column(String(2048))
    timestamp           = Column(DateTime)
    sum_all_single      = Column(Integer)
    sum_all_average     = Column(Integer)
    sum_wca_single      = Column(Integer)
    sum_wca_average     = Column(Integer)
    sum_non_wca_single  = Column(Integer)
    sum_non_wca_average = Column(Integer)
    wca_kinchrank       = Column(Float)
    non_wca_kinchrank   = Column(Float)
    all_kinchrank       = Column(Float)

    # Save the data as a dict so we don't have to deserialize it every time it's
    # retrieved for the same object
    __data_as_dict = None

    def __get_site_rankings_data_as_dict(self):
        """ Deserializes data field to json to return site rankings info as a dict.
        If key == event_id, value = (single, single_site_ranking, average, average_site_ranking)"""

        if not self.__data_as_dict:
            # The keys (event ID) get converted to strings when serializing to json.
            # We need them as ints, so iterate through the deserialized dict, building a new
            # one with ints as keys instead of strings. Return that.
            site_rankings = dict()
            for key, value in json.loads(self.data).items():
                site_rankings[int(key)] = value

            self.__data_as_dict = site_rankings

        return self.__data_as_dict


    def get_site_rankings_and_pbs(self):
        """ Returns just the site rankings and PBs information in dictionary format, without the
        sum of ranks information. """

        return self.__get_site_rankings_data_as_dict()


    def get_combined_sum_of_ranks(self):
        """ Returns SumOfRanks data structure for combined sum of ranks. """

        return SumOfRanks(single=self.sum_all_single, average=self.sum_all_average,
            username=self.user.username)


    def get_WCA_sum_of_ranks(self):
        """ Returns SumOfRanks data structure for combined sum of ranks. """

        return SumOfRanks(single=self.sum_wca_single, average=self.sum_wca_average,
            username=self.user.username)


    def get_non_WCA_sum_of_ranks(self):
        """ Returns SumOfRanks data structure for combined sum of ranks. """

        return SumOfRanks(single=self.sum_non_wca_single, average=self.sum_non_wca_average,
            username=self.user.username)


    def get_combined_kinchrank(self):
        """ Returns Kinchranks data structure for combined Kinchrank (WCA + non-WCA). """

        return Kinchranks(username=self.user.username, value=self.all_kinchrank,
            display=format(self.all_kinchrank, '.3f'))


    def get_WCA_kinchrank(self):
        """ Returns Kinchranks data structure for WCA event Kinchrank. """

        return Kinchranks(username=self.user.username, value=self.wca_kinchrank,
            display=format(self.wca_kinchrank, '.3f'))


    def get_non_WCA_kinchrank(self):
        """ Returns Kinchranks data structure for non-WCA event Kinchrank. """

        return Kinchranks(username=self.user.username, value=self.non_wca_kinchrank,
            display=format(self.non_wca_kinchrank, '.3f'))


class UserSolve(Model):
    """ A user's solve for a specific scramble, in a specific event, at a competition.
    Solve times are in centiseconds (ex: 1234 = 12.34s)."""

    __tablename__  = 'user_solves'
    __table_args__ = (
        DB.UniqueConstraint('scramble_id', 'user_event_results_id', name='unique_scramble_user_results'),
    )

    id                    = Column(Integer, primary_key=True)
    time                  = Column(Integer)
    is_dnf                = Column(Boolean, default=False)
    is_inspection_dnf     = Column(Boolean, default=False)
    is_plus_two           = Column(Boolean, default=False)
    scramble_id           = Column(Integer, ForeignKey('scrambles.id'))
    user_event_results_id = Column(Integer, ForeignKey('user_event_results.id'))
    UserEventResults      = relationship("UserEventResults")
    fmc_explanation       = Column(Text)

    def get_total_time(self):
        """ Returns the solve's time with +2s penalty counted, if applicable. """
        return (self.time + 200) if self.is_plus_two else self.time


    def get_friendly_time(self):
        """Returns a user-friendly representation of this solve's overall time, including penalties. """

        if not self.time:
            return ''

        # TODO: handle blind DNFs, which show "DNF(time here)"
        if self.is_dnf:
            return 'DNF'

        total_time = self.get_total_time()

        if self.UserEventResults.is_fmc:
            converted_value = int(total_time) / 100
            if converted_value == int(converted_value):
                converted_value = int(converted_value)
            return converted_value

        if self.UserEventResults.is_mbld:
            return str(MbldSolve(total_time))

        converted_to_friendly = convert_centiseconds_to_friendly_time(total_time)
        if self.is_plus_two:
            converted_to_friendly = converted_to_friendly + '+'

        return converted_to_friendly


class UserSetting(Model):
    """ A user's preferences. """

    __tablename__ = 'user_settings'
    id            = Column(Integer, primary_key=True)
    user_id       = Column(Integer, ForeignKey('users.id'), index=True)
    user          = relationship('User', primaryjoin=user_id == User.id)
    setting_code  = Column(String(128), index=True)
    setting_value = Column(String(128), index=True)


class SCSGiftCodePool(Model):
    """ A pool of SCS gift codes to be used for sending to weekly competition winners. """

    __tablename__ = 'scs_gift_codes'
    id            = Column(Integer, primary_key=True)
    gift_code     = Column(String(32))
    used          = Column(Boolean)


class WeeklyCodeRecipientResolution():
    """ Possible status values for deciding to award a gift code to a weekly comp participant. """
    Pending    = 'pending'
    Confirmed  = 'confirmed'
    Denied     = 'denied'


class WeeklyCodeRecipientConfirmDeny(Model):
    """ A record that tracks a specific user potentially chosen as the winner of the SCS gift code
    for participating in weekly competitions. This can be confirmed, denied, or still pending
    review by an admin. """

    __tablename__ = 'weekly_code_recipient_confirm_deny'
    id            = Column(Integer, primary_key=True)
    user_id       = Column(Integer, ForeignKey('users.id'), index=True)
    comp_id       = Column(Integer, ForeignKey('competitions.id'), index=True)
    gift_code_id  = Column(Integer, ForeignKey('scs_gift_codes.id'), index=True)
    confirm_code  = Column(String(36))
    deny_code     = Column(String(36))
    resolution    = Column(Enum("pending", "confirmed", "denied", name="resolution"), default="pending")
