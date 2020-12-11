""" Routes related to a user's events settings. """

from flask import render_template, redirect, url_for, request
from flask_login import current_user

from app import app
from app.persistence.events_manager import get_all_events
from app.persistence.settings_manager import get_setting_for_user,\
    set_new_settings_for_user, SettingCode
from app.persistence.user_manager import get_user_by_username

# -------------------------------------------------------------------------------------------------

@app.route('/settings/events', methods=['GET', 'POST'])
def events_settings():
    """ A route for showing a editing a user's preferred events. """

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    user = get_user_by_username(current_user.username)
    return __handle_post(user, request.form) if request.method == 'POST' else __handle_get(user)


def __handle_get(user):
    """ Handles displaying a user's event settings for edit. """

    hidden_event_setting = get_setting_for_user(user.id, SettingCode.HIDDEN_EVENTS)

    # Parse out the hidden event IDs into a separate list so we handle that separately
    if hidden_event_setting:
        hidden_event_ids = {int(s) for s in hidden_event_setting.split(',')}
    else:
        hidden_event_ids = set()

    return render_template("user/settings/events_settings.html",
                           is_mobile=request.MOBILE,
                           hidden_event_ids=hidden_event_ids,
                           events=get_all_events())


def __handle_post(user, form):
    """ Handles editing a user's event settings. """

    # Grab form fields which begin with `hidden_event_`, and then filter down to just
    # the ones that are valued true. These are IDs for events which the user wants to hide.
    event_settings = [(k, v) for k, v in form.items() if k.startswith('hidden_event_')]
    hidden_event_ids = [k.replace('hidden_event_', '') for k, v in event_settings if v == 'true']

    new_settings = { SettingCode.HIDDEN_EVENTS: ','.join(hidden_event_ids) }
    set_new_settings_for_user(user.id, new_settings)

    return redirect(url_for('index'))
