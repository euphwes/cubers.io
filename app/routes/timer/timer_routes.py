""" Routes related to the timer page. """

import json
from random import choice as random_choice

from flask import render_template, request
from flask_login import current_user

from app import app
from app.persistence.models import EventFormat
from app.persistence.comp_manager import get_comp_event_by_id
from app.persistence.settings_manager import SettingCode, SettingType, TRUE_STR,\
    get_default_values_for_settings, get_bulk_settings_for_user_as_dict, get_setting_type
from app.persistence.user_results_manager import get_event_results_for_user
from app.util.events.resources import get_event_names_without_scramble_previews, EVENT_FMC,\
    EVENT_MBLD

# -------------------------------------------------------------------------------------------------

DNF = 'DNF'

DEFAULT_SECONDS = '0'
DEFAULT_CENTIS  = '00'

TIMER_TEMPLATE_MOBILE_MAP = {
    True:  'timer/mobile/timer_page.html',
    False: 'timer/timer_page.html',
}

ERR_MSG_NO_SUCH_EVENT = "Can't find a competition event with ID {comp_event_id}."
ERR_MSG_INACTIVE_COMP = 'This event belongs to a competition which has ended.'

NOT_YET_SOLVED = '—'
NOT_YET_SOLVED_ARRAY = [[NOT_YET_SOLVED, -1, False, False]]

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

# Just for fun, mix up the encouragement portion of the DNF result messaging.
ENCOURAGEMENTS = [
    "Don't give up!",
    "Keep trying!",
    "Better luck next time!",
    "Never give up, never surrender!",
    "Hang in there.",
    "Stay strong.",
    "Believe in yourself."
]

EMOJI = [
    ":-(",
    ":(",
    "⊙︿⊙",
    "●︿●",
    ":-/"
]

MSG_RESULTS_COMPLETE            = "{excl}!\nYou've finished {event_name} with {result_type} of {result}."
MSG_RESULTS_COMPLETE_TWO_PBS    = "{excl}!\nYou've finished {event_name} with a PB average of {average} and a PB single of {single}!"
MSG_RESULTS_COMPLETE_PB_SINGLE  = "{excl}!\nYou've finished {event_name} with a PB single of {result}!"
MSG_RESULTS_COMPLETE_PB_AVERAGE = "{excl}!\nYou've finished {event_name} with a PB average of {result}!"
MSG_RESULTS_DNF                 = "You've finished {event_name} with a DNF result.\n{encouragement}"
MSG_RESULTS_DNF_EMOJI           = "{emoji}"

EVENT_FORMAT_RESULTS_TYPE_MAP = {
    EventFormat.Bo3: 'a best single',
    EventFormat.Bo1: 'a result',
    EventFormat.Ao5: 'an average',
    EventFormat.Mo3: 'a mean',
}

SUBTYPE_TIMER  = 'subtype_timer'
SUBTYPE_MANUAL = 'subtype_manual'
SUBTYPE_FMC    = 'subtype_fmc'
SUBTYPE_MBLD   = 'subtype_mbld'

# -------------------------------------------------------------------------------------------------

@app.route('/compete/<int:comp_event_id>')
def timer_page(comp_event_id, gather_info_for_live_refresh=False):
    """ It's the freakin' timer page. """

    # Retrieve the specified competition event
    comp_event = get_comp_event_by_id(comp_event_id)
    if not comp_event:
        return (ERR_MSG_NO_SUCH_EVENT.format(comp_event_id=comp_event_id), 404)

    # Verify it's for the actve competition
    comp = comp_event.Competition
    if not comp.active:
        return (ERR_MSG_INACTIVE_COMP, 400)

    event_name = comp_event.Event.name
    event_format = comp_event.Event.eventFormat
    event_description = comp_event.Event.description

    # Get the user's settings, and specifically pull the setting to determine
    # whether or not to hide the scramble preview
    settings = __get_user_settings(current_user)
    hide_scramble_preview = settings[SettingCode.HIDE_SCRAMBLE_PREVIEW]
    show_shapes_background = settings[SettingCode.ENABLE_MOVING_SHAPES_BG]

    # Grab the user's event results (if any)
    user_results = get_event_results_for_user(comp_event_id, current_user)

    # Get a list of user-readable user solve times
    user_solves, last_solve = __build_user_solves_list(user_results, comp_event.Event.totalSolves,
                                                       comp_event.scrambles)

    # Split last_solve into min/seconds and centiseconds
    # TODO: comment this more thoroughly, and put into its own function
    last_seconds   = DEFAULT_SECONDS
    last_centis    = DEFAULT_CENTIS
    hide_timer_dot = False
    if last_solve:
        if event_name == EVENT_FMC.name:
            hide_timer_dot = True
            last_seconds   = last_solve
            last_centis    = ''
        elif event_name == EVENT_MBLD.name:
            pass
        else:
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
                                                       comp_event.scrambles, event_name,
                                                       event_format)
    scramble_id, scramble_text, scramble_index = scramble_info

    # Build up the page title, consisting of the event name and competition title
    alternative_title = PAGE_TITLE_TEMPLATE.format(event_name=event_name,
                                                   comp_title=comp.title)

    # Determine if we should display a scramble preview for this event
    show_scramble_preview = event_name not in get_event_names_without_scramble_previews()

    # Determine button states
    button_state_info = __determine_button_states(user_results, scramble_index)

    # Grab the comment (if any) from the user results (if any), otherwise default to an empty string
    comment = user_results.comment if user_results else ''

    # Determine if the event has been completed by this user
    is_complete_flag = user_results.is_complete if user_results else False
    num_solves_done  = len(user_results.solves) if user_results else 0
    is_complete = __determine_is_complete(is_complete_flag, event_format, num_solves_done)

    # Determine the timer page subtype (timer, manual time entry, FMC manual entry, or MBLD)
    page_subtype = __determine_page_subtype(event_name, settings)

    if gather_info_for_live_refresh:
        # Only a caller coming from one of the persistence routes should go through this path.
        # Build up a dictionary of relevant information so the timer page can be re-rendered
        # with up-to-date information about the state of the timer page
        timer_page_render_info = {
            'button_state_info': button_state_info,
            'scramble_text':     scramble_text,
            'scramble_id':       scramble_id,
            'user_solves':       user_solves,
            'last_seconds':      last_seconds,
            'last_centis':       last_centis,
            'hide_timer_dot':    hide_timer_dot,
            'is_complete':       is_complete,
            'comment':           comment,
            'last_solve':        last_solve
        }
        return json.dumps(timer_page_render_info)

    return render_template(TIMER_TEMPLATE_MOBILE_MAP[request.MOBILE], scramble_text=scramble_text,
        scramble_id=scramble_id, comp_event_id=comp_event_id, event_name=event_name,
        alternative_title=alternative_title, user_solves=user_solves, button_states=button_state_info,
        show_scramble_preview=show_scramble_preview, last_solve=last_solve, last_seconds=last_seconds,
        last_centis=last_centis, hide_timer_dot=hide_timer_dot, comment=comment,
        is_complete=is_complete, settings=settings, page_subtype=page_subtype,
        hide_scramble_preview=hide_scramble_preview, show_shapes_background=show_shapes_background,
        event_description=event_description)

# -------------------------------------------------------------------------------------------------

def __build_user_solves_list(user_results, event_total_solves, scrambles):
    """ Returns a list in user-readable form of the user's current solves as a list of
    [displayable_time, solve_id, is_dnf, is_plus_two] units, plus the most recent solve's friendly
    display time. """

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
                user_solves[i] = [solve.get_friendly_time(), solve.id, str(solve.is_dnf).lower(),
                                  str(solve.is_plus_two).lower(), scramble.scramble]

    return user_solves, user_results.solves[-1].get_friendly_time()


def __determine_is_complete(is_complete_flag, event_format, num_solves_completed):
    """ Determine if the event is complete from the POV of the timer page; we don't want to disable
    time entry, even if the user has 1 BLD solve out of 3 and we consider it complete for the purpose
    of the leaderboards. """

    if event_format == EventFormat.Bo3:
        return num_solves_completed == 3

    return is_complete_flag


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
            if solve[0] == NOT_YET_SOLVED:
                first_unsolved_idx = i
                break

    # If the first unsolved index is set to -1, it means all the solves are done.
    # Instead of scramble text, return a message indicating they're done, possibly
    # with some additional info about PBs or whatever.
    if first_unsolved_idx == -1:
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
    previous_was_dnf            = False
    previous_was_plus_two       = False
    previous_was_inspection_dnf = False

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

        previous_was_dnf            = solves[previous_idx].is_dnf
        previous_was_plus_two       = solves[previous_idx].is_plus_two
        previous_was_inspection_dnf = solves[previous_idx].is_inspection_dnf

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
        # can apply DNF when there's at least one solve, and the previous wasn't an inspection DNF
        BTN_ENABLED: bool(solves) and (not previous_was_inspection_dnf),
        BTN_ACTIVE:  previous_was_dnf  # DNF button is toggled on if previous solve was DNF
    }

    # Let's determine the plus two button's state
    plus_two_btn_state = {
        # can apply +2 when there's at least one solve, and the previous wasn't an inspection DNF
        BTN_ENABLED: bool(solves) and (not previous_was_inspection_dnf),
        BTN_ACTIVE:  previous_was_plus_two  # +2 button is toggled on if previous solve was +2
    }

    return {
        BTN_DNF:      dnf_btn_state,
        BTN_UNDO:     undo_btn_state,
        BTN_COMMENT:  comment_btn_state,
        BTN_PLUS_TWO: plus_two_btn_state,
    }


def __determine_page_subtype(event_name, settings):
    """ Determines the timer page sub-type (timer, manual time entry, FMC manual entry, or MBLD)
    based on the current event and the user's settings. """

    if event_name == EVENT_FMC.name:
        return SUBTYPE_FMC

    if event_name == EVENT_MBLD.name:
        return SUBTYPE_MBLD

    return SUBTYPE_MANUAL if settings[SettingCode.DEFAULT_TO_MANUAL_TIME] else SUBTYPE_TIMER


def __build_done_message(user_results, event_name, event_format):
    """ Builds a message to display to the user about their complete results.
    Mention PBs if any. """

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

    if user_results.friendly_result() == 'DNF':
        if random_choice(range(100)) < 20:
            return MSG_RESULTS_DNF_EMOJI.format(emoji=random_choice(EMOJI))
        else:
            return MSG_RESULTS_DNF.format(
                event_name=event_name,
                encouragement=random_choice(ENCOURAGEMENTS)
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
    SettingCode.USE_INSPECTION_TIME,
    SettingCode.HIDE_INSPECTION_TIME,
    SettingCode.USE_INSPECTION_AUDIO_WARNING,
    SettingCode.HIDE_SCRAMBLE_PREVIEW,
    SettingCode.ENABLE_MOVING_SHAPES_BG,
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
    SettingCode.USE_CUSTOM_FTO_COLORS,
    SettingCode.CUSTOM_FTO_COLOR_U,
    SettingCode.CUSTOM_FTO_COLOR_F,
    SettingCode.CUSTOM_FTO_COLOR_R,
    SettingCode.CUSTOM_FTO_COLOR_D,
    SettingCode.CUSTOM_FTO_COLOR_B,
    SettingCode.CUSTOM_FTO_COLOR_L,
    SettingCode.CUSTOM_FTO_COLOR_BL,
    SettingCode.CUSTOM_FTO_COLOR_BR,
    SettingCode.USE_CUSTOM_SQUAN_COLORS,
    SettingCode.CUSTOM_SQUAN_COLOR_U,
    SettingCode.CUSTOM_SQUAN_COLOR_F,
    SettingCode.CUSTOM_SQUAN_COLOR_R,
    SettingCode.CUSTOM_SQUAN_COLOR_D,
    SettingCode.CUSTOM_SQUAN_COLOR_B,
    SettingCode.CUSTOM_SQUAN_COLOR_L,
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
