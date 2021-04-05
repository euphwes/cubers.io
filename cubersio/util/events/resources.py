""" Resources for data related to events. """

from typing import List, Optional

from pyTwistyScrambler import scrambler333, scrambler222, scrambler444, scrambler555, scrambler666, scrambler777,\
    squareOneScrambler, megaminxScrambler, pyraminxScrambler, cuboidsScrambler, skewbScrambler, clockScrambler,\
    bigCubesScrambler, ftoScrambler, rexScrambler

from cubersio.util.events.scramblers.coll import get_coll_scramble
from cubersio.util.events.scramblers.internal import fmc_scrambler, mbld_scrambler, redi_scrambler, attack_scrambler,\
    fifteen_puzzle_scrambler, scrambler_333_relay, scrambler_234_relay
from cubersio.persistence.models import CompetitionEvent, Event


class EventDefinition:
    """ Encapsulates everything we need to know about an event. """

    def __init__(self, name, scramble_func, num_scrambles=5, is_weekly=True, is_wca=True, is_rotating=False):
        # TODO do we really need num_scrambles, and the is_weekly, is_wca_, is_rotating flags? Can this be in the event
        # database records instead?

        self.name = name
        self.scramble_func = scramble_func
        self.num_scrambles = num_scrambles
        self.is_weekly = is_weekly
        self.is_wca = is_wca
        self.is_rotating = is_rotating

    def get_scramble(self, *args):
        """ Returns a scramble for this event. """

        return self.scramble_func(*args)


class WCAEventDefinition(EventDefinition):
    def __init__(self, name, scramble_func, num_scrambles=5):
        super().__init__(name, scramble_func, num_scrambles, is_weekly=True, is_wca=True, is_rotating=False)


class WeeklyEventDefinition(EventDefinition):
    def __init__(self, name, scramble_func, num_scrambles=5):
        super().__init__(name, scramble_func, num_scrambles, is_weekly=True, is_wca=False, is_rotating=False)


class BonusEventDefinition(EventDefinition):
    def __init__(self, name, scramble_func, num_scrambles=5):
        super().__init__(name, scramble_func, num_scrambles, is_weekly=False, is_wca=False, is_rotating=True)


# WCA event definitions (current count = 18)
EVENT_2x2      = WCAEventDefinition("2x2", scrambler222.get_WCA_scramble)
EVENT_3x3      = WCAEventDefinition("3x3", scrambler333.get_WCA_scramble)
EVENT_4x4      = WCAEventDefinition("4x4", scrambler444.get_random_state_scramble)
EVENT_5x5      = WCAEventDefinition("5x5", scrambler555.get_WCA_scramble)
EVENT_6x6      = WCAEventDefinition("6x6", scrambler666.get_WCA_scramble, num_scrambles=3)
EVENT_7x7      = WCAEventDefinition("7x7", scrambler777.get_WCA_scramble, num_scrambles=3)
EVENT_3x3OH    = WCAEventDefinition("3x3OH", scrambler333.get_WCA_scramble)
EVENT_Square1  = WCAEventDefinition("Square-1", squareOneScrambler.get_WCA_scramble)
EVENT_Pyraminx = WCAEventDefinition("Pyraminx", pyraminxScrambler.get_WCA_scramble)
EVENT_Megaminx = WCAEventDefinition("Megaminx", megaminxScrambler.get_WCA_scramble)
EVENT_Skewb    = WCAEventDefinition("Skewb", skewbScrambler.get_WCA_scramble)
EVENT_Clock    = WCAEventDefinition("Clock", clockScrambler.get_WCA_scramble)
EVENT_3x3_Feet = WCAEventDefinition("3x3 With Feet", scrambler333.get_WCA_scramble)
EVENT_FMC      = WCAEventDefinition("FMC", fmc_scrambler, num_scrambles=3)
EVENT_3BLD     = WCAEventDefinition("3BLD", scrambler333.get_3BLD_scramble, num_scrambles=3)
EVENT_4BLD     = WCAEventDefinition("4BLD", scrambler444.get_4BLD_scramble, num_scrambles=3)
EVENT_5BLD     = WCAEventDefinition("5BLD", scrambler555.get_5BLD_scramble, num_scrambles=3)
EVENT_MBLD     = WCAEventDefinition("MBLD", mbld_scrambler, num_scrambles=3)

# Weekly non-WCA event definitions (current count = 3)
EVENT_2GEN = WeeklyEventDefinition("2GEN", scrambler333.get_2genRU_scramble)
EVENT_LSE  = WeeklyEventDefinition("LSE", scrambler333.get_2genMU_scramble)
EVENT_FTO  = WeeklyEventDefinition("FTO", ftoScrambler.get_multiple_random_state_scrambles)

# Rotating bonus event definitions (current count = 20)
EVENT_COLL      = BonusEventDefinition("COLL", get_coll_scramble)
EVENT_F2L       = BonusEventDefinition("F2L", scrambler333.get_WCA_scramble)
EVENT_Void      = BonusEventDefinition("Void Cube", scrambler333.get_3BLD_scramble)
EVENT_Mirror    = BonusEventDefinition("3x3 Mirror Blocks/Bump", scrambler333.get_WCA_scramble)
EVENT_Kilominx  = BonusEventDefinition("Kilominx", megaminxScrambler.get_WCA_scramble)
EVENT_4x4OH     = BonusEventDefinition("4x4 OH", scrambler444.get_random_state_scramble)
EVENT_3x3x2     = BonusEventDefinition("3x3x2", cuboidsScrambler.get_3x3x2_scramble)
EVENT_3x3x4     = BonusEventDefinition("3x3x4", cuboidsScrambler.get_3x3x4_scramble)
EVENT_3x3x5     = BonusEventDefinition("3x3x5", cuboidsScrambler.get_3x3x5_scramble)
EVENT_234Relay  = BonusEventDefinition("2-3-4 Relay", scrambler_234_relay, num_scrambles=1)
EVENT_333Relay  = BonusEventDefinition("3x3 Relay of 3", scrambler_333_relay, num_scrambles=1)
EVENT_PLLAttack = BonusEventDefinition("PLL Time Attack", attack_scrambler, num_scrambles=1)
EVENT_2BLD      = BonusEventDefinition("2BLD", scrambler222.get_WCA_scramble, num_scrambles=3)
EVENT_REDI      = BonusEventDefinition("Redi Cube", redi_scrambler)
EVENT_DINO      = BonusEventDefinition("Dino Cube", lambda: redi_scrambler(5))
EVENT_REX       = BonusEventDefinition("Rex Cube", rexScrambler.get_multiple_random_state_scrambles)
EVENT_2x2x3     = BonusEventDefinition("2x2x3", cuboidsScrambler.get_2x2x3_scramble)
EVENT_Fifteen   = BonusEventDefinition("15 Puzzle", fifteen_puzzle_scrambler)
EVENT_8x8       = BonusEventDefinition("8x8", bigCubesScrambler.get_8x8x8_scramble, num_scrambles=1)
EVENT_9x9       = BonusEventDefinition("9x9", bigCubesScrambler.get_9x9x9_scramble, num_scrambles=1)

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
    EVENT_FTO,
    EVENT_REX
]

# Important! Don't change how these weekly and bonus lists are built, we rely on the order.
WEEKLY_EVENTS = [event for event in __ALL_EVENTS if event.is_weekly]
BONUS_EVENTS = [event for event in __ALL_EVENTS if (not event.is_weekly) and event.is_rotating]
WCA_EVENTS = [event for event in __ALL_EVENTS if event.is_wca]
NON_WCA_EVENTS = [event for event in __ALL_EVENTS if not event.is_wca]

# Important! Don't change the order of these.
COLL_LIST = [
    'B1', 'B2', 'B3', 'B4', 'B5', 'B6',
    'C1', 'C2', 'C3', 'C4', 'C5', 'C6',
    'D1', 'D2', 'D3', 'D4', 'D5', 'D6',
    'E1', 'E2', 'E3', 'E4', 'E5', 'E6',
    'F1', 'F2', 'F3', 'F4', 'F5', 'F6',
    'G1', 'G2', 'G3', 'G4', 'G5', 'G6',
    'H1', 'H2', 'H3', 'H4'
]

# Events which do not support scramble preview
EVENTS_NO_SCRAMBLE_PREVIEW = [
    EVENT_2BLD,
    EVENT_3BLD,
    EVENT_4BLD,
    EVENT_5BLD,
    EVENT_MBLD,
    EVENT_3x3x5,
    EVENT_234Relay,
    EVENT_333Relay,
    EVENT_PLLAttack
]

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
    EVENT_REX,
    EVENT_Fifteen,
    EVENT_8x8,
    EVENT_9x9,
]


def sort_comp_events_by_global_sort_order(comp_events: List[CompetitionEvent]) -> List[CompetitionEvent]:
    """ Sorts a list of competition events by the global event order defined above. """

    ordered_comp_events = list()

    event_name_comp_event_map = {c.Event.name: c for c in comp_events}
    comp_event_names = set(event_name_comp_event_map.keys())

    for event in __GLOBAL_SORT_ORDER:
        if event.name in comp_event_names:
            ordered_comp_events.append(event_name_comp_event_map[event.name])

    return ordered_comp_events


def sort_events_by_global_sort_order(events: List[Event]) -> List[Event]:
    """ Sorts a list of events by the global event order defined above. """

    ordered_events = list()

    event_name_event_map = {e.name: e for e in events}
    comp_event_names = set(event_name_event_map.keys())

    for event in __GLOBAL_SORT_ORDER:
        if event.name in comp_event_names:
            ordered_events.append(event_name_event_map[event.name])

    return ordered_events


def get_bonus_events_rotation_starting_at(starting_index: int, count: int = 5) -> List[BonusEventDefinition]:
    """ Gets a list of `count` bonus events starting at the specified index. Use a doubled list
    of bonus events as a 'trick' to wrap around to the beginning if the starting index and count
    bring us past the end of the list. """

    double_wide = BONUS_EVENTS * 2
    return double_wide[starting_index: starting_index + count]


def get_bonus_events_without_current(bonus_events: List[BonusEventDefinition]) -> List[BonusEventDefinition]:
    """ Gets a list of the bonus events except for the current ones. """

    return [e for e in BONUS_EVENTS if e not in bonus_events]


def get_event_definition_for_name(event_name: str) -> Optional[EventDefinition]:
    """ Returns the event definition for the specified event name. """

    for event in __ALL_EVENTS:
        if event.name == event_name:
            return event

    return None
