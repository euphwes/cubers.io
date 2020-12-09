""" Routes related to a user's profile. """
# pylint: disable=line-too-long

from collections import OrderedDict

from flask import render_template, redirect, url_for, request
from flask_login import current_user

from app import app
from app.persistence.events_manager import get_all_events
from app.persistence.settings_manager import get_settings_for_user_for_edit,\
    set_new_settings_for_user, SettingCode, SettingType, FALSE_STR, TRUE_STR, get_color_defaults
from app.persistence.user_manager import get_user_by_username

# -------------------------------------------------------------------------------------------------

# These are the settings we want the user to be able to see on the settings edit page



HIDDEN_EVENT_SETTING = [
    SettingCode.HIDDEN_EVENTS
]

CUSTOM_CUBE_COLOR_SETTINGS = [
    SettingCode.USE_CUSTOM_CUBE_COLORS,
    SettingCode.CUSTOM_CUBE_COLOR_U,
    SettingCode.CUSTOM_CUBE_COLOR_F,
    SettingCode.CUSTOM_CUBE_COLOR_R,
    SettingCode.CUSTOM_CUBE_COLOR_D,
    SettingCode.CUSTOM_CUBE_COLOR_B,
    SettingCode.CUSTOM_CUBE_COLOR_L,
]

CUSTOM_PYRAMINX_COLOR_SETTINGS = [
    SettingCode.USE_CUSTOM_PYRAMINX_COLORS,
    SettingCode.CUSTOM_PYRAMINX_COLOR_F,
    SettingCode.CUSTOM_PYRAMINX_COLOR_L,
    SettingCode.CUSTOM_PYRAMINX_COLOR_R,
    SettingCode.CUSTOM_PYRAMINX_COLOR_D,
]

CUSTOM_MEGAMINX_COLOR_SETTINGS = [
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


CUSTOM_FTO_COLOR_SETTINGS = [
    SettingCode.USE_CUSTOM_FTO_COLORS,
    SettingCode.CUSTOM_FTO_COLOR_U,
    SettingCode.CUSTOM_FTO_COLOR_R,
    SettingCode.CUSTOM_FTO_COLOR_F,
    SettingCode.CUSTOM_FTO_COLOR_L,
    SettingCode.CUSTOM_FTO_COLOR_B,
    SettingCode.CUSTOM_FTO_COLOR_D,
    SettingCode.CUSTOM_FTO_COLOR_BR,
    SettingCode.CUSTOM_FTO_COLOR_BL,
]

__ALL_SETTINGS = CUSTOM_CUBE_COLOR_SETTINGS + CUSTOM_PYRAMINX_COLOR_SETTINGS
__ALL_SETTINGS += HIDDEN_EVENT_SETTING + CUSTOM_MEGAMINX_COLOR_SETTINGS
__ALL_SETTINGS += CUSTOM_FTO_COLOR_SETTINGS

# -------------------------------------------------------------------------------------------------

@app.route('/settings', methods=['GET', 'POST'])
def edit_settings():
    """ A route for showing a editing a user's personal settings. """

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    user = get_user_by_username(current_user.username)
    return __handle_post(user, request.form) if request.method == 'POST' else __handle_get(user)


def __handle_get(user):
    """ Handles displaying a user's settings for edit. """

    all_settings = get_settings_for_user_for_edit(user.id, __ALL_SETTINGS)

    settings_sections = OrderedDict([
        ("Timer Settings",        [s for s in all_settings if s.code in set(TIMER_SETTINGS)]),
        ("Reddit Settings",       [s for s in all_settings if s.code in set(REDDIT_SETTINGS)]),
        ("WCA Settings",          [s for s in all_settings if s.code in set(SHOW_WCA_ID_SETTING)]),
        ("Hidden Events",         [s for s in all_settings if s.code in set(HIDDEN_EVENT_SETTING)]),
        ("Custom Cube Color",     [s for s in all_settings if s.code in set(CUSTOM_CUBE_COLOR_SETTINGS)]),
        ("Custom Pyraminx Color", [s for s in all_settings if s.code in set(CUSTOM_PYRAMINX_COLOR_SETTINGS)]),
        ("Custom Megaminx Color", [s for s in all_settings if s.code in set(CUSTOM_MEGAMINX_COLOR_SETTINGS)]),
        ("Custom FTO Color",      [s for s in all_settings if s.code in set(CUSTOM_FTO_COLOR_SETTINGS)]),
    ])

    # Parse out the hidden event IDs into a separate list so we handle that separately
    hidden_event_setting = [s for s in all_settings if s.code == SettingCode.HIDDEN_EVENTS][0]
    hidden_event_ids = set([int(s) for s in hidden_event_setting.value.split(',')]) if hidden_event_setting.value else set()

    # If the user doesn't have Reddit account info, omit the Reddit Settings section
    if not user.reddit_id:
        del settings_sections['Reddit Settings']

    # If the user doesn't have WCA account info, omit the WCA Settings section
    if not user.wca_id:
        del settings_sections['WCA Settings']

    # Disable the relevant settings, if other setting values affect them
    disabled_settings = list()
    for setting in all_settings:
        if setting.type != SettingType.BOOLEAN:
            continue
        if bool(setting.affects):
            if setting.value == TRUE_STR and setting.opposite_affects:
                disabled_settings.extend(setting.affects)
            if setting.value == FALSE_STR and not setting.opposite_affects:
                disabled_settings.extend(setting.affects)

    default_colors = get_color_defaults()

    return render_template("user/settings.html", settings_sections=settings_sections,
                           disabled_settings=disabled_settings, default_colors=default_colors,
                           alternative_title="Preferences", is_mobile=request.MOBILE,
                           hidden_event_ids=hidden_event_ids, events=get_all_events())


def __handle_post(user, form):
    """ Handles editing a user's settings. """

    new_settings = { code: form.get(code) for code in __ALL_SETTINGS }

    # TODO comment this part a little better
    hidden_event_ids = list()
    for event_id, _ in [(k, v) for k, v in form.items() if k.startswith('hidden_event_') and v == 'true']:
        hidden_event_ids.append(event_id.replace('hidden_event_', ''))

    hidden_event_ids = ','.join(hidden_event_ids)
    new_settings[SettingCode.HIDDEN_EVENTS] = hidden_event_ids

    # TODO: handle validators failing here
    set_new_settings_for_user(user.id, new_settings)

    return redirect(url_for('index'))
