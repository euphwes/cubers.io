""" Routes related to the timer page. """

from random import choice as random_choice

from flask import render_template, request
from flask_login import current_user

from app import app
from app.persistence.models import EventFormat
from app.persistence.comp_manager import get_comp_event_by_id
from app.persistence.settings_manager import SettingCode, SettingType, TRUE_STR,\
    get_default_values_for_settings, get_bulk_settings_for_user_as_dict, get_setting_type
from app.persistence.user_results_manager import get_event_results_for_user

# -------------------------------------------------------------------------------------------------

DNF = 'DNF'

DEFAULT_SECONDS = '0'
DEFAULT_CENTIS  = '00'

TIMER_TEMPLATE_MOBILE_MAP = {
    True:  'timer/mobile/timer_page.html',
    False: 'timer/timer_page.html',
}

NO_SCRAMBLE_PREVIEW_EVENTS = ["2BLD", "3BLD", "4BLD", "5BLD", "Kilominx", "3x3 Mirror Blocks/Bump",
                              "3x3x4", "3x3x5", "2-3-4 Relay", "3x3 Relay of 3", "PLL Time Attack"]

ERR_MSG_NO_SUCH_EVENT = "Can't find a competition event with ID {comp_event_id}."
ERR_MSG_INACTIVE_COMP = 'This event belongs to a competition which has ended.'

NOT_YET_SOLVED = '—'
NOT_YET_SOLVED_ARRAY = [NOT_YET_SOLVED]

PAGE_TITLE_TEMPLATE = '{event_name} — {comp_title}'

BTN_DNF      = 'btn_dnf'
BTN_UNDO     = 'btn_undo'
BTN_COMMENT  = 'btn_comment'
BTN_PLUS_TWO = 'btn_plus_two'

BTN_ACTIVE  = 'btn_active'
BTN_ENABLED = 'btn_enabled'

# Just for fun, mix up the first part of the 'your event is complete' messaging
EXCLAMATIONS = [
    'Wow',
    'Amazing',
    'Incredible',
    'Sweet',
    'Awesome',
    'Tubular',
    'Phenomenal',
    'Dude',
    'Crazy',
    'Nice'
]

MSG_RESULTS_COMPLETE            = "{excl}!\nYou've finished {event_name} with {result_type} of {result}."
MSG_RESULTS_COMPLETE_TWO_PBS    = "{excl}!\nYou've finished {event_name} with a PB average of {average} and a PB single of {single}!"
MSG_RESULTS_COMPLETE_PB_SINGLE  = "{excl}!\nYou've finished {event_name} with a PB single of {result}!"
MSG_RESULTS_COMPLETE_PB_AVERAGE = "{excl}!\nYou've finished {event_name} with a PB average of {result}!"

EVENT_FORMAT_RESULTS_TYPE_MAP = {
    EventFormat.Bo3: 'a best single',
    EventFormat.Bo1: 'a result',
    EventFormat.Ao5: 'an average',
    EventFormat.Mo3: 'a mean',
}

# -------------------------------------------------------------------------------------------------

@app.route('/compete/<int:comp_event_id>')
def timer_page(comp_event_id):
    """ It's the freakin' timer page. """

    # Retrieve the specified competition event
    comp_event = get_comp_event_by_id(comp_event_id)
    if not comp_event:
        return (ERR_MSG_NO_SUCH_EVENT.format(comp_event_id=comp_event_id), 404)

    # Verify it's for the actve competition
    comp = comp_event.Competition
    if not comp.active:
        return (ERR_MSG_INACTIVE_COMP, 400)

    # Grab the user's event results (if any)
    user_results = get_event_results_for_user(comp_event_id, current_user)

    # Get a list of user-readable user solve times
    user_solves, last_solve = __build_user_solves_list(user_results, comp_event.Event.totalSolves,
                                                       comp_event.scrambles)

    # Split last_solve into min/seconds and centiseconds
    last_seconds   = DEFAULT_SECONDS
    last_centis    = DEFAULT_CENTIS
    hide_timer_dot = False
    if last_solve:
        if last_solve == DNF:
            hide_timer_dot = True
            last_seconds   = DNF
            last_centis    = ''
        else:
            last_seconds = last_solve.split('.')[0]
            last_centis  = last_solve.split('.')[1]

    # Determine the scramble ID, scramble text, and index for the next unsolved scramble.
    # If all solves are done, substitute in some sort of message in place of the scramble text
    scramble_info = __determine_scramble_id_text_index(user_results, user_solves,
                                                       comp_event.scrambles, comp_event.Event.name,
                                                       comp_event.Event.eventFormat)
    scramble_id, scramble_text, scramble_index = scramble_info

    # Build up the page title, consisting of the event name and competition title
    alternative_title = PAGE_TITLE_TEMPLATE.format(event_name=comp_event.Event.name,
                                                   comp_title=comp.title)

    # Determine if we should display a scramble preview for this event
    show_scramble_preview = comp_event.Event.name not in NO_SCRAMBLE_PREVIEW_EVENTS

    # Determine button states
    button_state_info = __determine_button_states(user_results, scramble_index)

    # Grab the comment (if any) from the user results (if any), otherwise default to an empty string
    comment = user_results.comment if user_results else ''

    # Determine if the event has been completed by this user
    is_complete = user_results.is_complete if user_results else False

    # Get the user's settings
    settings = __get_user_settings(current_user)

    return render_template(TIMER_TEMPLATE_MOBILE_MAP[request.MOBILE], scramble_text=scramble_text,
        scramble_id=scramble_id, comp_event_id=comp_event_id, event_name=comp_event.Event.name,
        alternative_title=alternative_title, user_solves=user_solves, button_states=button_state_info,
        show_scramble_preview=show_scramble_preview, last_solve=last_solve, last_seconds=last_seconds,
        last_centis=last_centis, hide_timer_dot=hide_timer_dot, comment=comment,
        is_complete=is_complete, settings=settings)

# -------------------------------------------------------------------------------------------------

def __build_user_solves_list(user_results, event_total_solves, scrambles):
    """ Builds up a list in user-readable form of the user's current solve times. """

    # Begin with an array of 'not yet solved' entries, with a length equal to the number of solves
    # this event has.
    user_solves = NOT_YET_SOLVED_ARRAY * event_total_solves

    # If the user doesn't have an event results record yet, they don't have any solves, so just
    # return all 'not yet solved' entries
    if not user_results:
        return user_solves, None

    # Otherwise, iterate over all the solves and scrambles, and if there is a solve for a given
    # scramble, put the solve's user-friendly time in the corresponding slot in the array
    for i, scramble in enumerate(scrambles):
        for solve in user_results.solves:
            if scramble.id == solve.scramble_id:
                user_solves[i] = solve.get_friendly_time()

    return user_solves, user_results.solves[-1].get_friendly_time()


def __determine_scramble_id_text_index(user_results, user_solves_list, scrambles, event_name,
                                       event_format):
    """ Based on the user's current results, and the list of scrambles for this competition event,
    determine the "active" scramble ID and its text. """

    # To hold the index within the event's scrambles of the first scramble not yet solved.
    # The "default" state should be that the user doesn't yet have an event results record, and
    # therefore doesn't have any solves, and therefore the first unsolved scramble is just the
    # very first one
    first_unsolved_idx = 0

    # If the user has results, iterate over the user solves list to find the the first "solve time"
    # which is 'not yet solved' indicator. Remember that index.
    if user_results:
        first_unsolved_idx = -1
        for i, solve in enumerate(user_solves_list):
            if solve == NOT_YET_SOLVED:
                first_unsolved_idx = i
                break

    # If the first unsolved index is set to -1, it means all the solves are done.
    # Instead of scramble text, return a message indicating they're done, possibly
    # with some additional info about PBs or whatever.
    if first_unsolved_idx == -1:
        # TODO -- determine the right message to put here
        scramble_text = __build_done_message(user_results, event_name, event_format)
        scramble_id = -1

    # Otherwise grab the scramble ID and text of the next unsolved scramble
    else:
        scramble_text = scrambles[first_unsolved_idx].scramble
        scramble_id = scrambles[first_unsolved_idx].id

    return scramble_id, scramble_text, first_unsolved_idx


def __determine_button_states(user_results, scramble_index):
    """ Determine the states (enabled/disabled, and active/inactive) of all control buttons
    (undo, +2, DNF, comment) depending on the current state of the user's event results and the
    individual solves. """

    # Assume the previous solve (if any) had no penalties by default
    previous_was_dnf      = False
    previous_was_plus_two = False

    # Get a shorter variable to access the user's solves
    solves = user_results.solves if user_results else None

    # If there are any solves, check the previous one for the actual penalties
    if solves:
        # If the current scramble index is -1, that means all solves are completed, so the
        # "previous" solve is just the last one in the list (at -1, because it wraps backwards)
        if scramble_index == -1:
            previous_idx = -1
        # Otherwise the previous solve is the one before the current scramble index
        else:
            previous_idx = scramble_index - 1

        previous_was_dnf      = solves[previous_idx].is_dnf
        previous_was_plus_two = solves[previous_idx].is_plus_two

    # Let's determine the comment button's state
    comment_btn_state = {
        BTN_ENABLED: bool(user_results),  # can enter comments once they have a results record
        BTN_ACTIVE:  False                # comment button isn't a toggle, no need to be active
    }

    # Let's determine the undo button's state
    undo_btn_state = {
        BTN_ENABLED: bool(solves),  # can undo when there's at least one solve
        BTN_ACTIVE:  False          # undo button isn't a toggle, no need to be active
    }

    # Let's determine the DNF button's state
    dnf_btn_state = {
        BTN_ENABLED: bool(solves),      # can apply DNF when there's at least one solve
        BTN_ACTIVE:  previous_was_dnf  # DNF button is toggled on if previous solve was DNF
    }

    # Let's determine the plus two button's state
    plus_two_btn_state = {
        BTN_ENABLED: bool(solves),           # can apply +2 when there's at least one solve
        BTN_ACTIVE:  previous_was_plus_two  # +2 button is toggled on if previous solve was +2
    }

    return {
        BTN_DNF:      dnf_btn_state,
        BTN_UNDO:     undo_btn_state,
        BTN_COMMENT:  comment_btn_state,
        BTN_PLUS_TWO: plus_two_btn_state,
    }


def __build_done_message(user_results, event_name, event_format):
    """ Builds a message to display to the user about their complete results. Mention PBs if any. """

    if user_results.was_pb_single and user_results.was_pb_average:
        return MSG_RESULTS_COMPLETE_TWO_PBS.format(
            excl=random_choice(EXCLAMATIONS),
            event_name=event_name,
            average=user_results.friendly_average(),
            single=user_results.friendly_single()
        )

    if user_results.was_pb_single:
        return MSG_RESULTS_COMPLETE_PB_SINGLE.format(
            excl=random_choice(EXCLAMATIONS),
            event_name=event_name,
            result=user_results.friendly_single()
        )

    if user_results.was_pb_average:
        return MSG_RESULTS_COMPLETE_PB_AVERAGE.format(
            excl=random_choice(EXCLAMATIONS),
            event_name=event_name,
            result=user_results.friendly_average()
        )

    return MSG_RESULTS_COMPLETE.format(
        excl=random_choice(EXCLAMATIONS),
        event_name=event_name,
        result_type=EVENT_FORMAT_RESULTS_TYPE_MAP[event_format],
        result=user_results.friendly_result()
    )

# -------------------------------------------------------------------------------------------------

# These are the settings relevant to the operation of the main cubers.io application
SETTINGS_TO_POPULATE = [
    SettingCode.DEFAULT_TO_MANUAL_TIME,
    SettingCode.HIDE_RUNNING_TIMER,
    SettingCode.HIDE_INSPECTION_TIME,
    SettingCode.USE_INSPECTION_TIME,
    SettingCode.USE_CUSTOM_CUBE_COLORS,
    SettingCode.CUSTOM_CUBE_COLOR_U,
    SettingCode.CUSTOM_CUBE_COLOR_F,
    SettingCode.CUSTOM_CUBE_COLOR_R,
    SettingCode.CUSTOM_CUBE_COLOR_D,
    SettingCode.CUSTOM_CUBE_COLOR_B,
    SettingCode.CUSTOM_CUBE_COLOR_L,
    SettingCode.USE_CUSTOM_PYRAMINX_COLORS,
    SettingCode.CUSTOM_PYRAMINX_COLOR_D,
    SettingCode.CUSTOM_PYRAMINX_COLOR_L,
    SettingCode.CUSTOM_PYRAMINX_COLOR_F,
    SettingCode.CUSTOM_PYRAMINX_COLOR_R,
    SettingCode.USE_CUSTOM_MEGAMINX_COLORS,
    SettingCode.CUSTOM_MEGAMINX_COLOR_1,
    SettingCode.CUSTOM_MEGAMINX_COLOR_2,
    SettingCode.CUSTOM_MEGAMINX_COLOR_3,
    SettingCode.CUSTOM_MEGAMINX_COLOR_4,
    SettingCode.CUSTOM_MEGAMINX_COLOR_5,
    SettingCode.CUSTOM_MEGAMINX_COLOR_6,
    SettingCode.CUSTOM_MEGAMINX_COLOR_7,
    SettingCode.CUSTOM_MEGAMINX_COLOR_8,
    SettingCode.CUSTOM_MEGAMINX_COLOR_9,
    SettingCode.CUSTOM_MEGAMINX_COLOR_10,
    SettingCode.CUSTOM_MEGAMINX_COLOR_11,
    SettingCode.CUSTOM_MEGAMINX_COLOR_12,
]

def __get_user_settings(user):
    """ Retrieves certain settings for use in the front-end. If there is no logged-in user, just
    retrieve default values for these settings. """

    if user:
        settings = get_bulk_settings_for_user_as_dict(user.id, SETTINGS_TO_POPULATE)
    else:
        settings = get_default_values_for_settings(SETTINGS_TO_POPULATE)

    # Convert boolean settings back to actual booleans
    for code, value in settings.items():
        if get_setting_type(code) == SettingType.BOOLEAN:
            settings[code] = value == TRUE_STR

    return settings
