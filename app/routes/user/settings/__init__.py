""" Common logic for settings-related routes. """

from flask import render_template, redirect, url_for, request

from app.persistence.settings_manager import get_settings_for_user_for_edit,\
    set_new_settings_for_user

# -------------------------------------------------------------------------------------------------

def __handle_get(user, settings_list, template_path):
    """ Display's a user's settings for edit. """

    return render_template(template_path,
                           settings = get_settings_for_user_for_edit(user.id, settings_list),
                           is_mobile = request.MOBILE)


def __handle_post(user, form, settings_list):
    """ Accept updated values for a user's settings and persist them. """

    new_settings = { code: form.get(code) for code in settings_list }
    set_new_settings_for_user(user.id, new_settings)

    return redirect(url_for('index'))
