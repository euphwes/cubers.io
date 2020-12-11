""" Common logic for settings-related routes. """

from http import HTTPStatus
from json import loads

from flask import render_template, redirect, url_for, request
from flask_login import current_user

from app import app
from app.persistence.settings_manager import get_settings_for_user_for_edit,\
    set_new_settings_for_user
from app.routes import api_login_required

# -------------------------------------------------------------------------------------------------

def __handle_get(user, settings_list, template_path):
    """ Display's a user's settings for edit. """

    return render_template(template_path,
                           settings = get_settings_for_user_for_edit(user.id, settings_list),
                           is_mobile = request.MOBILE)


@app.route('/settings/bool/save', methods=['POST'])
@api_login_required
def save_radio_settings():
    """ Saves the user's boolean preferences. """

    set_new_settings_for_user(current_user.id, loads(request.data))
    return ('', HTTPStatus.OK)
