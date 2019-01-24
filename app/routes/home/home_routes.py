""" Routes related to the main page. """

from flask import render_template, request, redirect, url_for
from flask_login import current_user

from app import CUBERS_APP
from app.persistence import comp_manager
from app.persistence.settings_manager import get_default_value_for_setting, get_setting_for_user,\
    SettingCode
from app.persistence.user_manager import get_user_by_username
from app.persistence.user_results_manager import get_event_results_for_user
from app.persistence.models import EventFormat

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route('/')
def index():
    """ Main page for the app. Shows cards for every event in the current competition."""

    if (not current_user.is_authenticated) and (not 'nologin' in request.args):
        return redirect(url_for(".prompt_login"))

    comp = comp_manager.get_active_competition()

    # If somebody is logged in, get that user so we can pre-fill the events data later.
    user = get_user_by_username(current_user.username) if current_user.is_authenticated else None

    # Get the user's relevant user settings, otherwise get defaults
    settings = get_user_settings(user)

    # This `events_for_json` dictionary is rendered into the page as a Javascript object, to be
    # pulled in by the main JS app's events data manager. Keys are competitionEvent ID and the
    # values are a dictionary containing the event name, event ID, event format, user comment,
    # and scrambles. The scrambles here a dictionary themselves containing the scramble ID, actual
    # scramble text, and has a placeholder for any complete user times to be filled in.
    events_for_json = dict()

    # Iterate over each competition event in this event, get the dict representation of it
    # that can be used in the front end to render everything. If there is a logged-in user,
    # fill that event dict with info about that user's completed solves, comments, etc
    for comp_event in comp.events:
        event_dict = comp_event.to_front_end_consolidated_dict()
        fill_user_data_for_event(user, event_dict)
        events_for_json[str(comp_event.id)] = event_dict

    # Build a list of competition events in this comp, ordered by their event ID
    # This ordering ensures events are ordered relative to each other in the same way each comp
    ordered_comp_events = list([comp_event for comp_event in comp.events])
    ordered_comp_events.sort(key=lambda c: c.event_id)

    # Record which events are complete and which are incomplete, so we can render the event cards
    # on the front end directly with the correct completion status (checkmark for complete, clock
    # for started but incomplete). Otherwise we need to calculate that after the page loads and
    # there's a fugly flicker when we apply those styles to the event cards
    complete_events = dict()
    incomplete_events = dict()
    for comp_event_id, event in events_for_json.items():
        if event.get(STATUS, '') == STATUS_COMPLETE:
            complete_events[int(comp_event_id)] = event
        elif event.get(STATUS, '') == STATUS_INCOMPLETE:
            incomplete_events[int(comp_event_id)] = event

    # Phew finally we can just render the page
    # pylint: disable=C0330
    return render_template('index.html', current_competition=comp, events_data=events_for_json,
        ordered_comp_events=ordered_comp_events, complete_events=complete_events,
        incomplete_events=incomplete_events, comp_id=comp.id, settings=settings)


@CUBERS_APP.route('/prompt_login')
def prompt_login():
    """ Prompts the user to login for the best experience. """

    comp = comp_manager.get_active_competition()
    return render_template('prompt_login/prompt_login.html', current_competition=comp)

# -------------------------------------------------------------------------------------------------

# The front-end dictionary keys
COMMENT        = 'comment'
SOLVES         = 'scrambles' # Because the times are paired with the scrambles in the front end
TIME           = 'time'
SCRAMBLE_ID    = 'id'
IS_DNF         = 'isDNF'
IS_PLUS_TWO    = 'isPlusTwo'
COMP_EVENT_ID  = 'comp_event_id'
STATUS         = 'status'
SUMMARY        = 'summary'
SINGLE         = 'single'
AVERAGE        = 'average'
RESULT         = 'result'
WAS_PB_SINGLE  = 'wasPbSingle'
WAS_PB_AVERAGE = 'wasPbAverage'
EVENT_FORMAT   = 'event_format'
BLIND_STATUS   = 'blind_status'

# Completeness status
STATUS_COMPLETE   = 'complete'
STATUS_INCOMPLETE = 'incomplete'

def fill_user_data_for_event(user, event_data):
    """ Checks if the user has a UserEventResults for this competition event. If they do, aggregate
    their data (user comment, solve times, solve penalty flags, etc) into the event data dictionary
    being passed to the front end so it's available at render-time and available to the JS app's
    events data manager.  """

    # If there's no logged in user, there's nothing to fill in
    if not user:
        return

    # Get UserEventResults for this competition event and user.
    # If there are no results, there's nothing to fill in, so we can just bail.
    results = get_event_results_for_user(event_data[COMP_EVENT_ID], user)
    if not results:
        return

    # Remember various stats about the userEventResults, so we can use it up front
    event_data[COMMENT]        = results.comment
    event_data[SUMMARY]        = results.times_string
    event_data[RESULT]         = results.friendly_result()
    event_data[SINGLE]         = results.friendly_single()
    event_data[AVERAGE]        = results.friendly_average()
    event_data[WAS_PB_SINGLE]  = results.was_pb_single
    event_data[WAS_PB_AVERAGE] = results.was_pb_average

    # Record a "blind status" flag for blind events that helps determine whether to display the
    # "done" messaging in the timer screen. The messaging should only be shown for blind events
    # if all 3 solves have been done, and we're sure the results have been calculated against
    # all 3 solves.
    if event_data[EVENT_FORMAT] == EventFormat.Bo3:
        num_solves = len(results.solves)
        event_data[BLIND_STATUS] = STATUS_COMPLETE if num_solves == 3 else STATUS_INCOMPLETE

    # Iterate through all the solves completed by the user, matching them to a scramble in
    # the events data. Record the time and penalty information so we have it up front.
    for solve in results.solves:
        for scramble in event_data[SOLVES]:
            if scramble[SCRAMBLE_ID] != solve.scramble_id:
                continue
            scramble[TIME]        = solve.time
            scramble[IS_DNF]      = solve.is_dnf
            scramble[IS_PLUS_TWO] = solve.is_plus_two

    # If the UserEventResults indicates the user has completed the event, then set the event status
    # to complete so we can stick the nice pleasing checkmark on the card at render time
    if results.is_complete:
        event_data[STATUS]  = STATUS_COMPLETE

    # If the event is not complete but has some solves, set the status as 'incomplete' so we can
    # render the clock thing
    elif bool(list(results.solves)):
        event_data[STATUS] = STATUS_INCOMPLETE

# -------------------------------------------------------------------------------------------------

def get_user_settings(user):
    """ Retrieves certain settings for use in the front-end. If there is no logged-in user, just
    retrieve default values for these settings. """

    # These are the settings relevant to the operation of the main cubers.io application
    settings_to_populate = [SettingCode.DEFAULT_TO_MANUAL_TIME, SettingCode.HIDE_RUNNING_TIMER,\
        SettingCode.USE_INSPECTION_TIME]

    # If there is a logged-in user, get their settings. Otherwise just get default values
    retrieve_setting = lambda code: get_setting_for_user(user.id, code) if user \
        else get_default_value_for_setting

    # Send back a dictionary of setting codes and their values
    return { code: retrieve_setting(code) for code in settings_to_populate }
