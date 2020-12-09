""" Routes related to a user's timer settings. """

from flask import redirect, url_for, request
from flask_login import current_user

from app import app
from app.persistence.settings_manager import SettingCode
from app.persistence.user_manager import get_user_by_username

from . import __handle_post, __handle_get

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
    if request.method == 'POST':
        __handle_post(user, request.form, __TIMER_SETTINGS)
        
    return __handle_get(user, __TIMER_SETTINGS, 'user/settings/timer_settings.html')
