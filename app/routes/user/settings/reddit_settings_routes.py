""" Routes related to a user's Reddit settings. """

from flask import redirect, url_for, request
from flask_login import current_user

from app import app
from app.persistence.settings_manager import SettingCode
from app.persistence.user_manager import get_user_by_username

from . import __handle_post, __handle_get

# -------------------------------------------------------------------------------------------------

__REDDIT_SETTINGS = [
    SettingCode.REDDIT_COMP_NOTIFY,
    SettingCode.REDDIT_RESULTS_NOTIFY,
]

# -------------------------------------------------------------------------------------------------

@app.route('/settings/reddit', methods=['GET', 'POST'])
def reddit_settings():
    """ A route for showing a editing a user's Reddit settings. """

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    user = get_user_by_username(current_user.username)
    if request.method == 'POST':
        __handle_post(user, request.form, __REDDIT_SETTINGS)

    return __handle_get(user, __REDDIT_SETTINGS, 'user/settings/reddit_settings.html')
