""" Routes related to the main page. """

from flask import render_template, redirect, url_for, jsonify
from flask_login import current_user

from app import app
from app.persistence import comp_manager
from app.persistence.events_manager import get_all_bonus_events_names
from app.persistence.user_results_manager import get_all_user_results_for_comp_and_user
from app.util.events.resources import sort_comp_events_by_global_sort_order
from app.persistence.settings_manager import get_setting_for_user, SettingCode, TRUE_STR

from app.routes.home.home_routes import __build_is_incomplete_func

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

    user = "none"
    if current_user:
        user = {
            'name': current_user.username,
            'profile_url': url_for('profile', username=current_user.username),
            'logout_url': url_for('logout'),
            'settings_url': url_for('edit_settings')
        }

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
        },
        'current_user': user
    }

    return jsonify(header_info)

@app.route("/api/competition-events")
def competition_events():
    """ Endpoint for retrieving the events of the current competition """

    comp = comp_manager.get_active_competition()
    comp_events = sort_comp_events_by_global_sort_order(comp.events)

    user_results = get_all_user_results_for_comp_and_user(comp.id, current_user.id)
    complete_events = { r.CompetitionEvent.id: r.friendly_result() for r in user_results if r.is_complete }

    is_incomplete_func = __build_is_incomplete_func(set(complete_events.keys()))
    incomplete_event_ids = set(r.CompetitionEvent.id for r in user_results if is_incomplete_func(r))

    bonus_event_names = set(get_all_bonus_events_names())
    bonus_events_ids = set(c.id for c in comp_events if c.Event.name in bonus_event_names)

    events = map(lambda event: api_event(event, complete_events, incomplete_event_ids, bonus_events_ids), comp_events)
    return jsonify(list(events))

def api_event(event, complete_events, incomplete_events, bonus_events):
    """ Method for getting detailed event information """

    name = event.Event.name
    if name == "3x3 Mirror Blocks/Bump":
        name = "Mirror Blocks"

    comp_id = event.Event.id

    complete = event.id in complete_events.keys()
    incomplete = event.id in incomplete_events

    status = "not_started"
    if complete:
        status = "complete"
    elif incomplete:
        status = "incomplete"

    bonus_event = event.id in bonus_events

    summary = complete_events.get(event.id, '')

    return {
        'name': name,
        'compId': comp_id,
        'competeLocation': url_for('timer_page', comp_event_id=event.id),
        'status': status,
        'bonusEvent': bonus_event,
        'summary': summary
    }
