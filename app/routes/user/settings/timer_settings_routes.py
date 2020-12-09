""" Routes related to a user's timer settings. """

from flask import render_template, redirect, url_for, request
from flask_login import current_user

from app import app
from app.persistence.settings_manager import get_settings_for_user_for_edit,\
    set_new_settings_for_user, SettingCode
from app.persistence.user_manager import get_user_by_username

# -------------------------------------------------------------------------------------------------

__TIMER_SETTINGS = [
    SettingCode.DEFAULT_TO_MANUAL_TIME,
    SettingCode.USE_INSPECTION_TIME,
    SettingCode.HIDE_INSPECTION_TIME,
    SettingCode.USE_INSPECTION_AUDIO_WARNING,
    SettingCode.HIDE_RUNNING_TIMER,
    SettingCode.HIDE_SCRAMBLE_PREVIEW,
    SettingCode.ENABLE_MOVING_SHAPES_BG,
]
# -------------------------------------------------------------------------------------------------

@app.route('/settings/timer', methods=['GET', 'POST'])
def timer_settings():
    """ A route for showing a editing a user's timer settings. """

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    user = get_user_by_username(current_user.username)
    return __handle_post(user, request.form) if request.method == 'POST' else __handle_get(user)


def __handle_get(user):
    """ Display's a user's timer settings for edit. """

    return render_template("user/settings/timer_settings.html",
                           settings = get_settings_for_user_for_edit(user.id, __TIMER_SETTINGS),
                           is_mobile = request.MOBILE)


def __handle_post(user, form):
    """ Accept updated values for a user's timer settings and persist them. """

    new_settings = { code: form.get(code) for code in __TIMER_SETTINGS }
    set_new_settings_for_user(user.id, new_settings)

    return redirect(url_for('index'))
