""" Routes related to displaying competition results. """

from flask import render_template, redirect, abort, request
from flask_login import current_user

from app import app
from app.persistence.comp_manager import get_comp_event_by_id
from app.persistence.settings_manager import SettingCode, SettingType, TRUE_STR,\
    get_default_values_for_settings, get_bulk_settings_for_user_as_dict, get_setting_type
from app.persistence.user_results_manager import get_event_results_for_user

# -------------------------------------------------------------------------------------------------

TIMER_TEMPLATE_MOBILE_MAP = {
    True:  'timer/mobile/timer_page.html',
    False: 'timer/timer_page.html',
}

NO_SCRAMBLE_PREVIEW_EVENTS = ["2BLD", "3BLD", "4BLD", "5BLD", "Kilominx", "3x3 Mirror Blocks/Bump",
                              "3x3x4", "3x3x5", "2-3-4 Relay", "3x3 Relay of 3", "PLL Time Attack"]

ERR_MSG_NO_SUCH_EVENT = "Can't find a competition event with ID {}."
ERR_MSG_INACTIVE_COMP = 'This event belongs to a competition which has ended.'

NOT_YET_SOLVED = '—'
NOT_YET_SOLVED_ARRAY = [NOT_YET_SOLVED]

# -------------------------------------------------------------------------------------------------

@app.route('/compete/<int:comp_event_id>')
def timer_page(comp_event_id):
    """ It's the freakin' timer page. """

    # Retrieve the specified competition event
    comp_event = get_comp_event_by_id(comp_event_id)
    if not comp_event:
        return (ERR_MSG_NO_SUCH_EVENT.format(comp_event_id), 404)

    # Verify it's for the actve competition
    comp = comp_event.Competition
    if not comp.active:
        return (ERR_MSG_INACTIVE_COMP, 400)

    # Grab the user's event results (if any)
    user_results = get_event_results_for_user(comp_event_id, current_user)

    # Get a list of user-readable user solve times
    user_solves = __build_user_solves_list(user_results, comp_event.Event.totalSolves,
                                           comp_event.scrambles)

    # Determine the scramble ID and scramble text for the next unsolved scramble.
    # If all solves are done, substitute in some sort of message in place of the scramble text
    scramble_info = __determine_scramble_id_and_text(user_results, user_solves,
                                                     comp_event.scrambles)
    scramble_id, scramble_text = scramble_info

    alternative_title = '{} — {}'.format(comp_event.Event.name, comp.title)

    show_scramble_preview = comp_event.Event.name not in NO_SCRAMBLE_PREVIEW_EVENTS

    return render_template(TIMER_TEMPLATE_MOBILE_MAP[request.MOBILE], scramble_text=scramble_text,
        scramble_id=scramble_id, comp_event_id=comp_event_id, event_name=comp_event.Event.name,
        alternative_title=alternative_title, user_solves=user_solves,
        show_scramble_preview=show_scramble_preview)

# -------------------------------------------------------------------------------------------------


def __build_user_solves_list(user_results, event_total_solves, scrambles):
    """ Builds up a list in user-readable form of the user's current solve times. """

    # TODO comment me

    user_solves = NOT_YET_SOLVED_ARRAY * event_total_solves

    if user_results:
        for i, scramble in enumerate(scrambles):
            for solve in user_results.solves:
                if scramble.id == solve.scramble_id:
                    user_solves[i] = solve.get_friendly_time()

    return user_solves


def __determine_scramble_id_and_text(user_results, user_solves_list, scrambles):
    """ Based on the user's current results, and the list of scrambles for this competition event,
    determine the "active" scramble ID and its text. TODO: if the event is complete, show a message
    of some sort """

    # TODO comment me

    first_unsolved_idx = 0

    if user_results:
        first_unsolved_idx = -1
        for i, solve in enumerate(user_solves_list):
            if solve == NOT_YET_SOLVED:
                first_unsolved_idx = i
                break

    if first_unsolved_idx != -1:
        scramble_text = scrambles[first_unsolved_idx].scramble
        scramble_id = scrambles[first_unsolved_idx].id
    else:
        scramble_text = "Congrats! You're done."
        scramble_id = -1

    return scramble_id, scramble_text

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
