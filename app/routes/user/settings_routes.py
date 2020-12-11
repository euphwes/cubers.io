""" Routes related to a user's profile. """
# pylint: disable=line-too-long

from collections import OrderedDict

from flask import render_template, redirect, url_for, request
from flask_login import current_user

from app import app
from app.persistence.events_manager import get_all_events
from app.persistence.settings_manager import get_settings_for_user_for_edit,\
    set_new_settings_for_user, SettingCode, SettingType, FALSE_STR, TRUE_STR, get_color_defaults
from app.persistence.user_manager import get_user_by_username

# -------------------------------------------------------------------------------------------------

# These are the settings we want the user to be able to see on the settings edit page

# -------------------------------------------------------------------------------------------------

@app.route('/settings', methods=['GET', 'POST'])
def edit_settings():
    """ A route for showing a editing a user's personal settings. """

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    user = get_user_by_username(current_user.username)
    return __handle_post(user, request.form) if request.method == 'POST' else __handle_get(user)


def __handle_get(user):
    """ Handles displaying a user's settings for edit. """

    all_settings = get_settings_for_user_for_edit(user.id, list())

    settings_sections = OrderedDict([])

    # Parse out the hidden event IDs into a separate list so we handle that separately
    hidden_event_setting = [s for s in all_settings if s.code == SettingCode.HIDDEN_EVENTS][0]
    hidden_event_ids = set([int(s) for s in hidden_event_setting.value.split(',')]) if hidden_event_setting.value else set()

    # If the user doesn't have Reddit account info, omit the Reddit Settings section
    if not user.reddit_id:
        del settings_sections['Reddit Settings']

    # If the user doesn't have WCA account info, omit the WCA Settings section
    if not user.wca_id:
        del settings_sections['WCA Settings']

    # Disable the relevant settings, if other setting values affect them
    disabled_settings = list()
    for setting in all_settings:
        if setting.type != SettingType.BOOLEAN:
            continue
        if bool(setting.affects):
            if setting.value == TRUE_STR and setting.opposite_affects:
                disabled_settings.extend(setting.affects)
            if setting.value == FALSE_STR and not setting.opposite_affects:
                disabled_settings.extend(setting.affects)

    default_colors = get_color_defaults()

    return render_template("user/settings.html", settings_sections=settings_sections,
                           disabled_settings=disabled_settings, default_colors=default_colors,
                           alternative_title="Preferences", is_mobile=request.MOBILE,
                           hidden_event_ids=hidden_event_ids, events=get_all_events())


def __handle_post(user, form):
    """ Handles editing a user's settings. """

    new_settings = { code: form.get(code) for code in list() }

    # TODO comment this part a little better
    hidden_event_ids = list()
    for event_id, _ in [(k, v) for k, v in form.items() if k.startswith('hidden_event_') and v == 'true']:
        hidden_event_ids.append(event_id.replace('hidden_event_', ''))

    hidden_event_ids = ','.join(hidden_event_ids)
    new_settings[SettingCode.HIDDEN_EVENTS] = hidden_event_ids

    # TODO: handle validators failing here
    set_new_settings_for_user(user.id, new_settings)

    return redirect(url_for('index'))
