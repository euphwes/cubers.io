""" Routes related to a user's events settings. """

from http import HTTPStatus
from json import loads

from flask import render_template, redirect, url_for, request
from flask_login import current_user

from app import app
from app.persistence.events_manager import get_all_events
from app.persistence.settings_manager import get_setting_for_user,\
    set_new_settings_for_user, SettingCode
from app.routes import api_login_required
from app.util.events.resources import sort_events_by_global_sort_order

# -------------------------------------------------------------------------------------------------

@app.route('/settings/events', methods=['GET'])
def events_settings():
    """ A route for editing a user's preferred events. """

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    # Load hidden event IDs out of comma-delimited string and into a list of ints
    hidden_event_setting = get_setting_for_user(current_user.id, SettingCode.HIDDEN_EVENTS)
    if hidden_event_setting:
        hidden_event_ids = [int(s) for s in hidden_event_setting.split(',')]
    else:
        hidden_event_ids = list()

    return render_template("user/settings/events_settings.html",
                           is_mobile=request.MOBILE,
                           hidden_event_ids=hidden_event_ids,
                           events=sort_events_by_global_sort_order(get_all_events()))


@app.route('/settings/events/save', methods=['POST'])
@api_login_required
def save_events_settings():
    """ Saves the user's event preferences. """

    hidden_event_ids = [str(i) for i in loads(request.data)]
    new_settings = {SettingCode.HIDDEN_EVENTS: ','.join(hidden_event_ids)}
    set_new_settings_for_user(current_user.id, new_settings)

    return ('', HTTPStatus.OK)
