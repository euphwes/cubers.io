""" Routes related to a user's profile. """

from flask import render_template, redirect, url_for, request
from flask_login import current_user

from app import CUBERS_APP
from app.persistence.settings_manager import get_settings_for_user_for_edit, set_setting_for_user,\
    SettingCode
from app.persistence.user_manager import get_user_by_username

# -------------------------------------------------------------------------------------------------

# These are the settings we want the user to be able to see on the settings edit page
VISIBLE_SETTINGS = [
    SettingCode.USE_INSPECTION_TIME,
    #SettingCode.HIDE_RUNNING_TIMER,
    #SettingCode.REDDIT_COMP_NOTIFY,
    #SettingCode.DEFAULT_TO_MANUAL_TIME
]

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route('/settings', methods=['GET','POST'])
def edit_settings():
    """ A route for showing a editing a user's personal settings. """

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    user = get_user_by_username(current_user.username)
    return __handle_post(user, request.form) if request.method == 'POST' else __handle_get(user)


def __handle_get(user):
    """ Handles displaying a user's settings for edit. """

    settings = get_settings_for_user_for_edit(user.id, VISIBLE_SETTINGS)
    return render_template("user/settings.html", settings=settings, alternative_title="Preferences")


def __handle_post(user, form):
    """ Handles editing a user's settings. """

    # NOTE: will need to handle validation errors on non-boolean settings in the future

    for setting_code in VISIBLE_SETTINGS:
        setting_value = form.get(setting_code)
        set_setting_for_user(user.id, setting_code, setting_value)

    return redirect(url_for('index'))
