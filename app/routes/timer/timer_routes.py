""" Routes related to displaying competition results. """

from random import choice

from flask import render_template, redirect, abort, request
from flask_login import current_user

from flask import render_template, request, redirect, url_for
from flask_login import current_user

from app import app
from app.persistence.comp_manager import get_comp_event_by_id
from app.persistence.settings_manager import SettingCode, SettingType, TRUE_STR,\
    get_default_values_for_settings, get_bulk_settings_for_user_as_dict, get_setting_type
from app.persistence.events_manager import get_all_bonus_events_names
from app.persistence.user_results_manager import get_event_results_for_user
from app.persistence.models import EventFormat
from app.util.events.resources import sort_comp_events_by_global_sort_order

# -------------------------------------------------------------------------------------------------

TIMER_TEMPLATE_MOBILE_MAP = {
    True:  'timer/mobile/timer_page.html',
    False: 'timer/timer_page.html',
}

# -------------------------------------------------------------------------------------------------

@app.route('/compete/<int:comp_event_id>')
def timer_page(comp_event_id):
    """ TODO: fill this for real.
    A temp route for working on timer page redesign outside of the real timer page. """

    comp_event = get_comp_event_by_id(comp_event_id)
    if not comp_event:
        return ("Can't find that event, oops.", 404)

    comp = comp_event.Competition
    if not comp.active:
        return ("Oops, that event belongs to a competition which has ended.", 400)

    scrambles = comp_event.scrambles
    user_results = get_event_results_for_user(comp_event_id, current_user)

    user_solves = ['—'] * comp_event.Event.totalSolves

    if user_results:
        for i, scramble in enumerate(scrambles):
            for solve in user_results.solves:
                if scramble.id == solve.scramble_id:
                    user_solves[i] = solve.get_friendly_time()

        first_unsolved_idx = -1
        for i, solve in enumerate(user_solves):
            if solve == '—':
                first_unsolved_idx = i
                break

    else:
        first_unsolved_idx = 0

    if first_unsolved_idx != -1:        
        print(first_unsolved_idx)
        scramble = comp_event.scrambles[first_unsolved_idx].scramble
    else:
        scramble = "Congrats! You're done."



    # TODO: on desktop, pad the solve times with nbsp to align them at the decimal like so:
    """
    <div class="solves_header">Solves</div>
    <div class="single_time">&nbsp;9.23&nbsp;</div>
    <div class="single_time">14.97&nbsp;</div>
    <div class="single_time">17.23+</div>
    <div class="single_time">DNF</div>
    <div class="single_time">—</div>
    """

    alternative_title = '{} — {}'.format(comp_event.Event.name, comp.title)

    return render_template(TIMER_TEMPLATE_MOBILE_MAP[request.MOBILE], scramble=scramble,
        alternative_title=alternative_title, user_solves=user_solves)

# -------------------------------------------------------------------------------------------------

# These are the settings relevant to the operation of the main cubers.io application
SETTINGS_TO_POPULATE = [
    SettingCode.DEFAULT_TO_MANUAL_TIME,
    SettingCode.HIDE_RUNNING_TIMER,
    SettingCode.HIDE_INSPECTION_TIME,
    SettingCode.USE_INSPECTION_TIME,
    SettingCode.USE_CUSTOM_CUBE_COLORS,
    SettingCode.CUSTOM_CUBE_COLOR_U,
    SettingCode.CUSTOM_CUBE_COLOR_F,
    SettingCode.CUSTOM_CUBE_COLOR_R,
    SettingCode.CUSTOM_CUBE_COLOR_D,
    SettingCode.CUSTOM_CUBE_COLOR_B,
    SettingCode.CUSTOM_CUBE_COLOR_L,
    SettingCode.USE_CUSTOM_PYRAMINX_COLORS,
    SettingCode.CUSTOM_PYRAMINX_COLOR_D,
    SettingCode.CUSTOM_PYRAMINX_COLOR_L,
    SettingCode.CUSTOM_PYRAMINX_COLOR_F,
    SettingCode.CUSTOM_PYRAMINX_COLOR_R,
    SettingCode.USE_CUSTOM_MEGAMINX_COLORS,
    SettingCode.CUSTOM_MEGAMINX_COLOR_1,
    SettingCode.CUSTOM_MEGAMINX_COLOR_2,
    SettingCode.CUSTOM_MEGAMINX_COLOR_3,
    SettingCode.CUSTOM_MEGAMINX_COLOR_4,
    SettingCode.CUSTOM_MEGAMINX_COLOR_5,
    SettingCode.CUSTOM_MEGAMINX_COLOR_6,
    SettingCode.CUSTOM_MEGAMINX_COLOR_7,
    SettingCode.CUSTOM_MEGAMINX_COLOR_8,
    SettingCode.CUSTOM_MEGAMINX_COLOR_9,
    SettingCode.CUSTOM_MEGAMINX_COLOR_10,
    SettingCode.CUSTOM_MEGAMINX_COLOR_11,
    SettingCode.CUSTOM_MEGAMINX_COLOR_12,
]

def get_user_settings(user):
    """ Retrieves certain settings for use in the front-end. If there is no logged-in user, just
    retrieve default values for these settings. """

    if user:
        settings = get_bulk_settings_for_user_as_dict(user.id, SETTINGS_TO_POPULATE)
    else:
        settings = get_default_values_for_settings(SETTINGS_TO_POPULATE)

    # Convert boolean settings back to actual booleans
    for code, value in settings.items():
        if get_setting_type(code) == SettingType.BOOLEAN:
            settings[code] = value == TRUE_STR

    return settings

    # -------------------------------------------------------------------------------------------------

# The front-end dictionary keys
COMMENT        = 'comment'
SOLVES         = 'scrambles'  # Because the times are paired with the scrambles in the front end
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
        event_data[STATUS] = STATUS_COMPLETE

    # If the event is not complete but has some solves, set the status as 'incomplete' so we can
    # render the clock thing
    elif bool(list(results.solves)):
        event_data[STATUS] = STATUS_INCOMPLETE