""" Routes related to a user's profile. """

from collections import OrderedDict

from flask import render_template, redirect, url_for, request
from flask_login import current_user

from app import app
from app.persistence.settings_manager import get_settings_for_user_for_edit,\
    set_new_settings_for_user, SettingCode, SettingType, FALSE_STR, TRUE_STR, get_color_defaults
from app.persistence.user_manager import get_user_by_username

# -------------------------------------------------------------------------------------------------

LOG_USER_VIEWED_SETTINGS  = '{} viewed settings page'
LOG_USER_UPDATED_SETTINGS = '{} updated settings'

# -------------------------------------------------------------------------------------------------

# These are the settings we want the user to be able to see on the settings edit page

TIMER_SETTINGS = [
    SettingCode.DEFAULT_TO_MANUAL_TIME,
    SettingCode.USE_INSPECTION_TIME,
    SettingCode.HIDE_INSPECTION_TIME,
    SettingCode.HIDE_RUNNING_TIMER,
    SettingCode.HIDE_SCRAMBLE_PREVIEW,
    SettingCode.ENABLE_MOVING_SHAPES_BG,
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

REDDIT_SETTINGS = [
    SettingCode.REDDIT_COMP_NOTIFY,
    SettingCode.REDDIT_RESULTS_NOTIFY,
]

__ALL_SETTINGS = REDDIT_SETTINGS + CUSTOM_CUBE_COLOR_SETTINGS + CUSTOM_PYRAMINX_COLOR_SETTINGS
__ALL_SETTINGS += CUSTOM_MEGAMINX_COLOR_SETTINGS + TIMER_SETTINGS

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

    # pylint: disable=line-too-long
    settings_sections = OrderedDict([
        ("Timer Page Preferences",      [s for s in all_settings if s.code in set(TIMER_SETTINGS)]),
        ("Reddit Preferences",          [s for s in all_settings if s.code in set(REDDIT_SETTINGS)]),
        ("Cube Color Preferences",      [s for s in all_settings if s.code in set(CUSTOM_CUBE_COLOR_SETTINGS)]),
        ("Pyraminx Color Preferences",  [s for s in all_settings if s.code in set(CUSTOM_PYRAMINX_COLOR_SETTINGS)]),
        ("Megaminx Color Preferences",  [s for s in all_settings if s.code in set(CUSTOM_MEGAMINX_COLOR_SETTINGS)]),
    ])

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

    app.logger.info(LOG_USER_VIEWED_SETTINGS.format(user.username))

    return render_template("user/settings.html", settings_sections=settings_sections,
                           disabled_settings=disabled_settings, default_colors=default_colors,
                           alternative_title="Preferences", is_mobile=request.MOBILE)


def __handle_post(user, form):
    """ Handles editing a user's settings. """

    # TODO: will need to handle validation errors on non-boolean settings in the future

    new_settings = { code: form.get(code) for code in __ALL_SETTINGS }
    set_new_settings_for_user(user.id, new_settings)

    app.logger.info(LOG_USER_UPDATED_SETTINGS.format(user.username), extra=new_settings)

    return redirect(url_for('index'))
