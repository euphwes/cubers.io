""" Common logic for settings-related routes. """

from http import HTTPStatus
from json import loads

from flask import render_template, request
from flask_login import current_user

from cubersio import app
from cubersio.persistence.settings_manager import get_settings_for_user_for_edit,\
    set_new_settings_for_user, SettingType, FALSE_STR, TRUE_STR
from cubersio.routes import api_login_required

# -------------------------------------------------------------------------------------------------

def __determine_disabled_settings(all_settings):
    """ Return a list of settings which should be disabled in the UI based on the user's current
    settings. """

    disabled_settings = list()
    for setting in all_settings:
        if setting.type != SettingType.BOOLEAN:
            continue
        if bool(setting.affects):
            if setting.value == TRUE_STR and setting.opposite_affects:
                disabled_settings.extend(setting.affects)
            if setting.value == FALSE_STR and not setting.opposite_affects:
                disabled_settings.extend(setting.affects)

    return disabled_settings


def __handle_get(user, settings_list, template_path):
    """ Display's a user's settings for edit. """

    settings = get_settings_for_user_for_edit(user.id, settings_list)

    return render_template(template_path,
                           settings = settings,
                           disabled_settings = __determine_disabled_settings(settings),
                           is_mobile = request.MOBILE)


@app.route('/settings/save', methods=['POST'])
@api_login_required
def save_settings():
    """ Saves the user's provided settings. """

    set_new_settings_for_user(current_user.id, loads(request.data))
    return ('', HTTPStatus.OK)
