""" Routes related to a user's profile. """

from flask import render_template, redirect, url_for, request
from flask_login import current_user

from app import CUBERS_APP
from app.persistence.settings_manager import get_settings_for_user_for_edit, set_setting_for_user,\
    SettingCode
from app.persistence.user_manager import get_user_by_username

# -------------------------------------------------------------------------------------------------

# These are the settings we want the user to be able to see on the settings edit page

TIMER_SETTINGS = set([
    SettingCode.USE_INSPECTION_TIME,
    #SettingCode.HIDE_RUNNING_TIMER,
    #SettingCode.DEFAULT_TO_MANUAL_TIME
])

REDDIT_SETTINGS = set([
    #SettingCode.REDDIT_COMP_NOTIFY,
])

__ALL_SETTINGS = REDDIT_SETTINGS | TIMER_SETTINGS

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

    all_settings = get_settings_for_user_for_edit(user.id, __ALL_SETTINGS)

    settings_sections = {
        "Timer Preferences":  [s for s in all_settings if s.code in TIMER_SETTINGS],
        "Reddit Preferences": [s for s in all_settings if s.code in REDDIT_SETTINGS],
    }

    return render_template("user/settings.html", settings_sections=settings_sections,
                           alternative_title="Preferences")


def __handle_post(user, form):
    """ Handles editing a user's settings. """

    # NOTE: will need to handle validation errors on non-boolean settings in the future

    # TODO: set all settings at once, so we don't have so many round-trips to the database
    for setting_code in __ALL_SETTINGS:
        setting_value = form.get(setting_code)
        set_setting_for_user(user.id, setting_code, setting_value)

    return redirect(url_for('index'))
