""" Routes related to a user's WCA settings. """

from flask import redirect, url_for
from flask_login import current_user

from app import app
from app.persistence.settings_manager import SettingCode

from . import __handle_get

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

    return __handle_get(current_user, __WCA_SETTINGS, 'user/settings/wca_settings.html')
