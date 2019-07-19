""" Routes related to the main page. """

from flask import render_template, redirect, url_for
from flask_login import current_user

from app import app
from app.persistence import comp_manager
from app.persistence.events_manager import get_all_bonus_events_names
from app.persistence.user_results_manager import get_all_user_results_for_comp_and_user
from app.util.events.resources import sort_comp_events_by_global_sort_order
from app.persistence.settings_manager import get_setting_for_user, SettingCode, TRUE_STR

from app.util.token import generate_token

# -------------------------------------------------------------------------------------------------

@app.route('/')
def index():
    """ Main page for the app. Shows cards for every event in the current competition."""

    if not current_user.is_authenticated:
        return redirect(url_for("prompt_login"))

    # Get the current competition
    comp = comp_manager.get_active_competition()
    if not comp:
        return "There are no competitions created yet. Go make one!"

    # Get all event results for the logged-in user
    user_results = get_all_user_results_for_comp_and_user(comp.id, current_user.id)

    # Get a dict of comp ID to result for all complete events
    complete_events = { r.CompetitionEvent.id: r.friendly_result() for r in user_results if r.is_complete }

    # Build a function which determines if a result is incomplete (solves are recorded, but enough yet to be complete)
    # Then build up a set of comp event IDs for incomplete events
    is_incomplete_func = __build_is_incomplete_func(set(complete_events.keys()))
    incomplete_event_ids = set(r.CompetitionEvent.id for r in user_results if is_incomplete_func(r))

    # Build a list of competition events in this comp. Initially order them by event ID, but then sort and group them
    # by WCA events first, non-WCA weekly events next, and then bonus events last. This ordering ensures events are
    # ordered relative to each other in the same way each comp
    comp_events = sort_comp_events_by_global_sort_order(comp.events)

    # Build a set of comp event IDs that are bonus events so we can mark them on the main page
    bonus_event_names = set(get_all_bonus_events_names())
    bonus_events_ids = set(c.id for c in comp_events if c.Event.name in bonus_event_names)

    # Determine whether to show moving shapes background
    show_shapes_background = get_setting_for_user(current_user.id, SettingCode.ENABLE_MOVING_SHAPES_BG)
    show_shapes_background = show_shapes_background == TRUE_STR

    generate_token()

    # Phew, finally we can render the page
    return render_template('index.html', current_competition=comp, comp_events=comp_events,
        complete_events=complete_events, incomplete_events=incomplete_event_ids, bonus_events_ids=bonus_events_ids,
        show_shapes_background=show_shapes_background)


@app.route('/prompt_login')
def prompt_login():
    """ Prompts the user to login for the best experience. """

    comp = comp_manager.get_active_competition()
    return render_template('prompt_login/prompt_login.html', current_competition=comp)

# -------------------------------------------------------------------------------------------------

def __build_is_incomplete_func(complete_ids):
    """ Returns a function which tells if the supplied UserEventResult is considered incomplete for
    the purpose of the main page; that is, it has some solves complete, but is not fully complete. """

    def __is_incomplete(result):
        return (result.CompetitionEvent.id not in complete_ids) and bool(result.solves)

    return __is_incomplete
