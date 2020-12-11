""" Routes related to a user's custom colors settings. """

from http import HTTPStatus
from json import loads

from flask import render_template, redirect, url_for, request
from flask_login import current_user

from app import app
from app.persistence.settings_manager import get_settings_for_user_for_edit, get_color_defaults,\
    set_new_settings_for_user, SettingCode
from app.routes import api_login_required

from . import __determine_disabled_settings

# -------------------------------------------------------------------------------------------------

__CUSTOM_CUBE_COLOR_SETTINGS = [
    SettingCode.USE_CUSTOM_CUBE_COLORS,
    SettingCode.CUSTOM_CUBE_COLOR_U,
    SettingCode.CUSTOM_CUBE_COLOR_F,
    SettingCode.CUSTOM_CUBE_COLOR_R,
    SettingCode.CUSTOM_CUBE_COLOR_D,
    SettingCode.CUSTOM_CUBE_COLOR_B,
    SettingCode.CUSTOM_CUBE_COLOR_L,
]

__CUSTOM_PYRAMINX_COLOR_SETTINGS = [
    SettingCode.USE_CUSTOM_PYRAMINX_COLORS,
    SettingCode.CUSTOM_PYRAMINX_COLOR_F,
    SettingCode.CUSTOM_PYRAMINX_COLOR_L,
    SettingCode.CUSTOM_PYRAMINX_COLOR_R,
    SettingCode.CUSTOM_PYRAMINX_COLOR_D,
]

__CUSTOM_MEGAMINX_COLOR_SETTINGS = [
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

__CUSTOM_FTO_COLOR_SETTINGS = [
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

__EVENT_SETTINGS_MAPPING = {
    'fto':      __CUSTOM_FTO_COLOR_SETTINGS,
    'cube':     __CUSTOM_CUBE_COLOR_SETTINGS,
    'pyraminx': __CUSTOM_PYRAMINX_COLOR_SETTINGS,
    'megaminx': __CUSTOM_MEGAMINX_COLOR_SETTINGS,
}

__EVENT_MSGS_MAPPING = {
    'fto': [
        'FTO (Face-Turning Octahedron)',
        'Customize the scramble preview for FTO by choosing custom colors below!'
    ],
    'cube': [
        'Cubes (NxN, Square-1, Skewb, etc)',
        'Customize the scramble preview for all cube events by choosing custom colors below!'
    ],
    'pyraminx': [
        'Pyraminx',
        'Customize the scramble preview for Pyraminx by choosing custom colors below!'
    ],
    'megaminx': [
        'Megaminx and Kilominx',
        'Customize the scramble preview for Megaminx and Kilominx by choosing custom colors below!'
    ],
}

__ERR_UNSUPPORTED_EVENT = 'Sorry! Custom colors for {} are not yet supported.'

# -------------------------------------------------------------------------------------------------

@app.route('/settings/colors/<event>', methods=['GET'])
def colors_settings(event):
    """ A route for editing a user's custom colors for scramble previews. """

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    if event not in __EVENT_SETTINGS_MAPPING.keys():
        return render_template('error.html', error_message=__ERR_UNSUPPORTED_EVENT.format(event))

    settings = get_settings_for_user_for_edit(current_user.id, __EVENT_SETTINGS_MAPPING[event])

    return render_template("user/settings/custom_colors_settings.html",
                           settings = settings,
                           disabled_settings = __determine_disabled_settings(settings),
                           is_mobile = request.MOBILE,
                           header_msg = __EVENT_MSGS_MAPPING[event],
                           default_colors = get_color_defaults())


@app.route('/settings/colors/save', methods=['POST'])
@api_login_required
def save_colors_settings():
    """ Saves the user's event preferences. """

    hidden_event_ids = [str(i) for i in loads(request.data)]
    new_settings = {SettingCode.HIDDEN_EVENTS: ','.join(hidden_event_ids)}
    set_new_settings_for_user(current_user.id, new_settings)

    return ('', HTTPStatus.OK)
