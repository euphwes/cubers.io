""" Routes related to the main page. """

from flask import render_template, redirect, url_for, jsonify
from flask_login import current_user

from app import app
from app.persistence import comp_manager
from app.persistence.events_manager import get_all_bonus_events_names
from app.persistence.user_results_manager import get_all_user_results_for_comp_and_user
from app.util.events.resources import sort_comp_events_by_global_sort_order
from app.persistence.settings_manager import get_setting_for_user, SettingCode, TRUE_STR

# -------------------------------------------------------------------------------------------------

@app.route("/api")
def get_general_info():
    header_info = {
        'title': 'example'
    }

    return jsonify(header_info)