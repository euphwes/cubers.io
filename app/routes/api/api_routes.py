""" Routes related to the main page. """

from flask import render_template, redirect, url_for, jsonify
from flask_login import current_user

from app import app
from app.persistence import comp_manager
from app.persistence.events_manager import get_all_bonus_events_names
from app.persistence.user_results_manager import get_all_user_results_for_comp_and_user
from app.util.events.resources import sort_comp_events_by_global_sort_order
from app.persistence.settings_manager import get_setting_for_user, SettingCode, TRUE_STR

from .constants import *

# -------------------------------------------------------------------------------------------------

@app.route("/api/header-info")
def get_header_info():
    """ Api endpoint for retrieving header information """

    comp = comp_manager.get_active_competition()
    title = None
    if comp.title:
        title = comp.title

    wca_events = list(map(lambda event: {
        'url': url_for('event_results', event_name=event),
        'name': event
    }, WCA_EVENTS))
    non_wca_events = list(map(lambda event: {
        'url': url_for('event_results', event_name=event),
        'name': event
    }, NON_WCA_EVENTS))

    sum_of_ranks = list(map(lambda sort: {
        'url': url_for('sum_of_ranks', sor_type=sort['sort']),
        'name': sort['name']
    }, SUM_OF_RANKS))

    header_info = {
        'compId': comp.id,
        'title': title,
        'recordsItems': {
            'wca': {
                'urls': wca_events,
                'title': 'WCA Events'
            },
            'nonWca': {
                'urls': non_wca_events,
                'title': 'Non-WCA Events'
            },
            'sum': {
                'urls': sum_of_ranks,
                'title': 'Sum of Ranks'
            }
        },
        'leaderboardItems': {
            'current': {
                'name': 'Current Competition',
                'url': '/leaderboards/{}'.format(comp.id)
            },
            'previous': {
                'name': 'Last Week\'s Competition',
                'url': '/leaderboards/{}'.format(comp.id - 1)
            },
            'all': {
                'name': 'All competitions',
                'url': url_for('results_list')
            }
        }
    }

    return jsonify(header_info)
