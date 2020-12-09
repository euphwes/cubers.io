""" Routes related to a user's Reddit settings. """

from flask import render_template, redirect, url_for, request
from flask_login import current_user

from app import app
from app.persistence.settings_manager import get_settings_for_user_for_edit,\
    set_new_settings_for_user, SettingCode
from app.persistence.user_manager import get_user_by_username

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
    return __handle_post(user, request.form) if request.method == 'POST' else __handle_get(user)


def __handle_get(user):
    """ Display's a user's WCA settings for edit. """

    return render_template("user/settings/wca_settings.html",
                           settings = get_settings_for_user_for_edit(user.id, __WCA_SETTINGS),
                           is_mobile = request.MOBILE)


def __handle_post(user, form):
    """ Accept updated values for a user's WCA settings and persist them. """

    new_settings = { code: form.get(code) for code in __WCA_SETTINGS }
    set_new_settings_for_user(user.id, new_settings)

    return redirect(url_for('index'))
