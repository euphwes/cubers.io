""" Resources for data related to events. """

from collections import OrderedDict

from pyTwistyScrambler import scrambler333, scrambler222, scrambler444, scrambler555, scrambler666, scrambler777,\
    squareOneScrambler, megaminxScrambler, pyraminxScrambler, cuboidsScrambler, skewbScrambler, clockScrambler,\
    bigCubesScrambler, ftoScrambler

from .coll import get_coll_scramble
from .scramblers.internal import fmc_scrambler, mbld_scrambler, redi_scrambler, fifteen_puzzle_scrambler,\
    scrambler_333_relay, scrambler_234_relay, attack_scrambler


class EventResource:
    """ Encapsulates everything we need to know about an event. """
    def __init__(self, name, scramble_func, num_scrambles, is_weekly, is_wca, is_rotating=False):
        self.name = name
        self.scramble_func = scramble_func
        self.num_scrambles = num_scrambles
        self.is_weekly = is_weekly
        self.is_wca = is_wca
        self.is_rotating = is_rotating

    def get_scramble(self, *args):
        """ Returns a scramble for this event. """
        return self.scramble_func(*args)


# Weekly event definitions (current count = 21)
EVENT_2x2       = EventResource("2x2", scrambler222.get_WCA_scramble, 5, True, True)
EVENT_3x3       = EventResource("3x3", scrambler333.get_WCA_scramble, 5, True, True)
EVENT_4x4       = EventResource("4x4", scrambler444.get_random_state_scramble, 5, True, True)
EVENT_5x5       = EventResource("5x5", scrambler555.get_WCA_scramble, 5, True, True)
EVENT_6x6       = EventResource("6x6", scrambler666.get_WCA_scramble, 3, True, True)
EVENT_7x7       = EventResource("7x7", scrambler777.get_WCA_scramble, 3, True, True)
EVENT_3BLD      = EventResource("3BLD", scrambler333.get_3BLD_scramble, 3, True, True)
EVENT_3x3OH     = EventResource("3x3OH", scrambler333.get_WCA_scramble, 5, True, True)
EVENT_Square1   = EventResource("Square-1", squareOneScrambler.get_WCA_scramble, 5, True, True)
EVENT_Pyraminx  = EventResource("Pyraminx", pyraminxScrambler.get_WCA_scramble, 5, True, True)
EVENT_Megaminx  = EventResource("Megaminx", megaminxScrambler.get_WCA_scramble, 5, True, True)
EVENT_Skewb     = EventResource("Skewb", skewbScrambler.get_WCA_scramble, 5, True, True)
EVENT_Clock     = EventResource("Clock", clockScrambler.get_WCA_scramble, 5, True, True)
EVENT_3x3_Feet  = EventResource("3x3 With Feet", scrambler333.get_WCA_scramble, 5, True, True)
EVENT_FMC       = EventResource("FMC", fmc_scrambler, 3, True, True)
EVENT_2GEN      = EventResource("2GEN", scrambler333.get_2genRU_scramble, 5, True, False)
EVENT_LSE       = EventResource("LSE", scrambler333.get_2genMU_scramble, 5, True, False)
EVENT_4BLD      = EventResource("4BLD", scrambler444.get_4BLD_scramble, 3, True, True)
EVENT_5BLD      = EventResource("5BLD", scrambler555.get_5BLD_scramble, 3, True, True)
EVENT_MBLD      = EventResource("MBLD", mbld_scrambler, 3, True, True)
EVENT_FTO       = EventResource("FTO", ftoScrambler.get_multiple_random_state_scrambles, 5, True, False)

# Bonus event definitions (current count = 19)
EVENT_COLL      = EventResource("COLL", get_coll_scramble, 5, False, False, is_rotating=True)
EVENT_F2L       = EventResource("F2L", scrambler333.get_WCA_scramble, 5, False, False, is_rotating=True)
EVENT_Void      = EventResource("Void Cube", scrambler333.get_3BLD_scramble, 5, False, False, is_rotating=True)
EVENT_Mirror    = EventResource("3x3 Mirror Blocks/Bump", scrambler333.get_WCA_scramble, 5, False, False, is_rotating=True)
EVENT_Kilominx  = EventResource("Kilominx", megaminxScrambler.get_WCA_scramble, 5, False, False, is_rotating=True)
EVENT_4x4OH     = EventResource("4x4 OH", scrambler444.get_random_state_scramble, 5, False, False, is_rotating=True)
EVENT_3x3x2     = EventResource("3x3x2", cuboidsScrambler.get_3x3x2_scramble, 5, False, False, is_rotating=True)
EVENT_3x3x4     = EventResource("3x3x4", cuboidsScrambler.get_3x3x4_scramble, 5, False, False, is_rotating=True)
EVENT_3x3x5     = EventResource("3x3x5", cuboidsScrambler.get_3x3x5_scramble, 5, False, False, is_rotating=True)
EVENT_234Relay  = EventResource("2-3-4 Relay", scrambler_234_relay, 1, False, False, is_rotating=True)
EVENT_333Relay  = EventResource("3x3 Relay of 3", scrambler_333_relay, 1, False, False, is_rotating=True)
EVENT_PLLAttack = EventResource("PLL Time Attack", attack_scrambler, 1, False, False, is_rotating=True)
EVENT_2BLD      = EventResource("2BLD", scrambler222.get_WCA_scramble, 3, False, False, is_rotating=True)
EVENT_REDI      = EventResource("Redi Cube", redi_scrambler, 5, False, False, is_rotating=True)
EVENT_DINO      = EventResource("Dino Cube", lambda: redi_scrambler(5), 5, False, False, is_rotating=True)
EVENT_2x2x3     = EventResource("2x2x3", cuboidsScrambler.get_2x2x3_scramble, 5, False, False, is_rotating=True)
EVENT_Fifteen   = EventResource("15 Puzzle", fifteen_puzzle_scrambler, 5, False, False, is_rotating=True)
EVENT_8x8       = EventResource("8x8", bigCubesScrambler.get_8x8x8_scramble, 1, False, False, is_rotating=True)
EVENT_9x9       = EventResource("9x9", bigCubesScrambler.get_9x9x9_scramble, 1, False, False, is_rotating=True)

# Important! Only add new events to the end, regardless of WCA or non-WCA status. We rely on the order here.
__ALL_EVENTS = [
    EVENT_2x2,
    EVENT_3x3,
    EVENT_4x4,
    EVENT_5x5,
    EVENT_6x6,
    EVENT_7x7,
    EVENT_3BLD,
    EVENT_3x3OH,
    EVENT_Square1,
    EVENT_Pyraminx,
    EVENT_Megaminx,
    EVENT_Skewb,
    EVENT_Clock,
    EVENT_3x3_Feet,
    EVENT_FMC,
    EVENT_3x3x2,
    EVENT_2GEN,
    EVENT_COLL,
    EVENT_Void,
    EVENT_333Relay,
    EVENT_F2L,
    EVENT_Mirror,
    EVENT_8x8,
    EVENT_3x3x4,
    EVENT_Kilominx,
    EVENT_4x4OH,
    EVENT_LSE,
    EVENT_3x3x5,
    EVENT_234Relay,
    EVENT_PLLAttack,
    EVENT_2BLD,
    EVENT_4BLD,
    EVENT_5BLD,
    EVENT_REDI,
    EVENT_9x9,
    EVENT_MBLD,
    EVENT_DINO,
    EVENT_2x2x3,
    EVENT_Fifteen,
    EVENT_FTO
]

# Important! Don't change how these weekly and bonus lists are built, we rely on the order.
__WEEKLY_EVENTS = [event for event in __ALL_EVENTS if event.is_weekly]
__BONUS_EVENTS = [event for event in __ALL_EVENTS if (not event.is_weekly) and event.is_rotating]
__WCA_EVENTS = [event for event in __ALL_EVENTS if event.is_wca]
__NON_WCA_EVENTS = [event for event in __ALL_EVENTS if not event.is_wca]

# Important! Don't change the order of these.
__COLL_LIST = [
    'B1', 'B2', 'B3', 'B4', 'B5', 'B6',
    'C1', 'C2', 'C3', 'C4', 'C5', 'C6',
    'D1', 'D2', 'D3', 'D4', 'D5', 'D6',
    'E1', 'E2', 'E3', 'E4', 'E5', 'E6',
    'F1', 'F2', 'F3', 'F4', 'F5', 'F6',
    'G1', 'G2', 'G3', 'G4', 'G5', 'G6',
    'H1', 'H2', 'H3', 'H4'
]

# Events which do not support scramble preview
__EVENTS_NO_SCRAMBLE_PREVIEW = [EVENT_2BLD, EVENT_3BLD, EVENT_4BLD, EVENT_5BLD, EVENT_MBLD,
                                EVENT_3x3x5, EVENT_234Relay, EVENT_333Relay, EVENT_PLLAttack]


__GLOBAL_SORT_ORDER = [
    # Weekly NxN
    EVENT_2x2,
    EVENT_3x3,
    EVENT_4x4,
    EVENT_5x5,
    EVENT_6x6,
    EVENT_7x7,

    # Weekly blind events
    EVENT_3BLD,
    EVENT_4BLD,
    EVENT_5BLD,
    EVENT_MBLD,

    # Weekly 3x3 variations
    EVENT_3x3OH,
    EVENT_3x3_Feet,

    # Weekly other
    EVENT_Square1,
    EVENT_Pyraminx,
    EVENT_Megaminx,
    EVENT_Skewb,
    EVENT_Clock,
    EVENT_FMC,

    # Weekly non-WCA
    EVENT_FTO,
    EVENT_2GEN,
    EVENT_LSE,

    # Bonus
    EVENT_2BLD,
    EVENT_Kilominx,
    EVENT_Mirror,
    EVENT_Void,
    EVENT_4x4OH,
    EVENT_2x2x3,
    EVENT_3x3x2,
    EVENT_3x3x4,
    EVENT_3x3x5,
    EVENT_234Relay,
    EVENT_333Relay,
    EVENT_PLLAttack,
    EVENT_COLL,
    EVENT_F2L,
    EVENT_REDI,
    EVENT_DINO,
    EVENT_Fifteen,
    EVENT_8x8,
    EVENT_9x9,
]

# -------------------------------------------------------------------------------------------------

def sort_comp_events_by_global_sort_order(comp_events):
    """ Sorts a list of competition events by the global event order defined above. """

    ordered_comp_events = list()

    event_name_comp_event_map = {c.Event.name: c for c in comp_events}
    comp_event_names = set(event_name_comp_event_map.keys())

    for event in __GLOBAL_SORT_ORDER:
        if event.name in comp_event_names:
            ordered_comp_events.append(event_name_comp_event_map[event.name])

    return ordered_comp_events


def sort_events_by_global_sort_order(events):
    """ Sorts a list of events by the global event order defined above. """

    ordered_events = list()

    event_name_event_map = {e.name: e for e in events}
    comp_event_names = set(event_name_event_map.keys())

    for event in __GLOBAL_SORT_ORDER:
        if event.name in comp_event_names:
            ordered_events.append(event_name_event_map[event.name])

    return ordered_events


def sort_site_rankings_by_global_sort_order(site_rankings, event_id_name_map):
    """ Sorts a list of site rankings by the global event order defined above. """

    ordered_rankings = OrderedDict()

    event_name_rankings_map = {event_id_name_map[r[0]]: r for r in site_rankings.items()}
    comp_event_names = set(event_name_rankings_map.keys())

    for event in __GLOBAL_SORT_ORDER:
        if event.name in comp_event_names:
            k, v = event_name_rankings_map[event.name]
            ordered_rankings[k] = v

    return ordered_rankings


def sort_event_id_name_map_by_global_sort_order(event_id_name_map):
    """ TODO """

    ordered_map = OrderedDict()

    for event in __GLOBAL_SORT_ORDER:
        for mapped_event_id, mapped_event_name in event_id_name_map.items():
            if mapped_event_name == event.name:
                ordered_map[mapped_event_id] = mapped_event_name

    return ordered_map

# -------------------------------------------------------------------------------------------------

def get_num_COLLs():
    """ Returns the length of the COLLs list. """

    return len(__COLL_LIST)


def get_num_bonus_events():
    """ Returns the length of the bonus events list. """

    return len(__BONUS_EVENTS)


def get_all_weekly_events():
    """ Return all the weekly events. """

    return __WEEKLY_EVENTS


def get_all_bonus_events():
    """ Return all the bonus events. """

    return __BONUS_EVENTS


def get_all_bonus_events_names():
    """ Return all the bonus events. """

    return [e.name for e in __BONUS_EVENTS]


def get_WCA_event_names():
    """ Returns the names of all WCA events. """

    return [e.name for e in __WCA_EVENTS]


def get_non_WCA_event_names():
    """ Returns the names of all non-WCA events. """

    return [e.name for e in __NON_WCA_EVENTS]


def get_bonus_events_rotation_starting_at(starting_index, count=5):
    """ Gets a list of `count` bonus events starting at the specified index. Use a doubled list
    of bonus events as a 'trick' to wrap around to the beginning if the starting index and count
    bring us past the end of the list. """

    double_wide = __BONUS_EVENTS * 2
    return double_wide[starting_index: starting_index + count]


def get_bonus_events_without_current(bonus_events):
    """ Gets a list of the bonus events except for the current ones. """

    return [e for e in __BONUS_EVENTS if e not in bonus_events]


def get_COLL_at_index(index):
    """ Gets the COLL at the specified index. """

    return __COLL_LIST[index]


def get_event_resource_for_name(event_name):
    """ Returns the event resource for the specified event name. """

    for event in __ALL_EVENTS:
        if event.name == event_name:
            return event

    return None


def get_event_names_without_scramble_previews():
    """ Returns the names of events without scramble previews. """

    return [e.name for e in __EVENTS_NO_SCRAMBLE_PREVIEW]
