""" Routes related to a user's WCA settings. """

from flask import redirect, url_for, request
from flask_login import current_user

from app import app
from app.persistence.settings_manager import SettingCode
from app.persistence.user_manager import get_user_by_username

from . import __handle_post, __handle_get

# -------------------------------------------------------------------------------------------------

__WCA_SETTINGS = [
    SettingCode.SHOW_WCA_ID
]

# -------------------------------------------------------------------------------------------------

@app.route('/settings/wca', methods=['GET', 'POST'])
def wca_settings():
    """ A route for showing a editing a user's WCA settings. """

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    user = get_user_by_username(current_user.username)
    if request.method == 'POST':
        __handle_post(user, request.form, __WCA_SETTINGS)

    return __handle_get(user, __WCA_SETTINGS, 'user/settings/wca_settings.html')
