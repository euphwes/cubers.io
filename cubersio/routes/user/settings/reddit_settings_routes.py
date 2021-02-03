""" Routes related to a user's Reddit settings. """

from flask import redirect, url_for
from flask_login import current_user

from cubersio import app
from cubersio.persistence.settings_manager import SettingCode

from . import __handle_get

# -------------------------------------------------------------------------------------------------

__REDDIT_SETTINGS = [
    SettingCode.REDDIT_COMP_NOTIFY,
    SettingCode.REDDIT_RESULTS_NOTIFY,
]

# -------------------------------------------------------------------------------------------------

@app.route('/settings/reddit', methods=['GET'])
def reddit_settings():
    """ A route for showing a editing a user's Reddit settings. """

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    return __handle_get(current_user, __REDDIT_SETTINGS, 'user/settings/reddit_settings.html')
