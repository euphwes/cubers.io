""" Routes related to the main page. """

from flask import render_template, request, redirect, url_for
from flask_login import current_user

from app import CUBERS_APP
from app.persistence import comp_manager
from app.persistence.user_manager import get_user_by_username
from app.persistence.user_results_manager import get_event_results_for_user

from app.routes.home.persistence_routes import build_summary

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route('/')
def index():
    """ Main page for the app. Shows cards for every event in the current competition."""

    if (not current_user.is_authenticated) and (not 'nologin' in request.args):
        return redirect(url_for(".prompt_login"))

    comp = comp_manager.get_active_competition()

    # Just make this DB query once, so we don't have to keep doing it
    # below when we fill in any existing user data.
    if current_user.is_authenticated:
        user = get_user_by_username(current_user.username)

    events_for_json = dict()
    for comp_event in comp.events:
        event = {
            'name':          comp_event.Event.name,
            'scrambles':     list(),
            'event_id':      comp_event.Event.id,
            'comp_event_id': comp_event.id,
            'comment':       '',
        }
        for scram in comp_event.scrambles:
            event['scrambles'].append({
                'id':       scram.id,
                'scramble': scram.scramble,
                'time':     0,
                'isPlusTwo': False,
                'isDNF': False,
            })

        if current_user.is_authenticated:
            event = fill_any_existing_user_data(user, event)

        events_for_json[str(comp_event.id)] = event

    ordered_comp_events = list([comp_event for comp_event in comp.events])
    ordered_comp_events.sort(key=lambda c: c.event_id)

    complete_events = dict()
    incomplete_events = dict()
    for comp_event_id, event in events_for_json.items():
        if event.get('status', '') == 'complete':
            complete_events[int(comp_event_id)] = event
        elif event.get('status', '') == 'incomplete':
            incomplete_events[int(comp_event_id)] = event

    return render_template('index.html', current_competition=comp, events_data=events_for_json,
                           ordered_comp_events=ordered_comp_events, complete_events=complete_events,
                           incomplete_events=incomplete_events)


@CUBERS_APP.route('/prompt_login')
def prompt_login():
    """ Prompts the user to login for the best experience. """
    comp = comp_manager.get_active_competition()
    return render_template('prompt_login/prompt_login.html', current_competition=comp)

# -------------------------------------------------------------------------------------------------

def fill_any_existing_user_data(user, event):
    """ Check """
    prev = get_event_results_for_user(event['comp_event_id'], user)
    if not prev:
        event['save_status'] = 'new'
        return event

    scrambles_completed = 0
    total_scrambles     = len(event['scrambles'])

    event['save_status'] = 'saved'
    event['comment'] = prev.comment
    for solve in prev.solves:
        scramble_id = solve.scramble_id
        for scram in event['scrambles']:
            if scram['id'] != scramble_id:
                continue
            scram['time'] = solve.time
            scram['isPlusTwo'] = solve.is_plus_two
            scram['isDNF'] = solve.is_dnf
            scrambles_completed += 1

    if scrambles_completed == total_scrambles:
        event['summary'] = build_summary(event)
        event['status']  = 'complete'
    elif scrambles_completed > 0:
        event['status']  = 'incomplete'

    return event
