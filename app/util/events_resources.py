""" Resources for data related to events. """

#pylint: disable=C0103

from pyTwistyScrambler import scrambler333, scrambler222, scrambler444, scrambler555,\
    scrambler666, scrambler777, squareOneScrambler, megaminxScrambler, pyraminxScrambler,\
    cuboidsScrambler, skewbScrambler, clockScrambler

# -------------------------------------------------------------------------------------------------

class Event:
    """ Encapsulates everything we need to know about an event. """

    def __init__(self, name, scramble_func, num_scrambles, is_wca, has_explanation=False, scramble_generator=False):
        self.name = name
        self.scramble_func = scramble_func
        self.num_scrambles = num_scrambles
        self.is_wca = is_wca
        self.has_explanation = has_explanation
        self.scramble_generator = scramble_generator

    def get_scrambles(self, *args):
        """ Gets the scrambles for this event. """

        if self.scramble_generator:
            return [s for s in self.scramble_func(*args)]
        
        return [self.scramble_func(*args) for _ in range(self.num_scrambles)]

# -------------------------------------------------------------------------------------------------

def COLL_scrambler(coll_num):
    """ Get a 'scramble' for the current COLL, which just says which one we're doing. """
    return "This week we're doing COLL {}".format(coll_num)

def scrambler_234_relay():
    """ Get a scramble for the 2-3-4 relay event. """
    yield scrambler222.get_WCA_scramble()
    yield scrambler333.get_WCA_scramble()
    yield scrambler444.get_WCA_scramble()

def scrambler_333_relay():
    """ Get a scramble for the 3x3 relay of 3 event. """
    yield scrambler333.get_WCA_scramble()
    yield scrambler333.get_WCA_scramble()
    yield scrambler333.get_WCA_scramble()

# -------------------------------------------------------------------------------------------------

# WCA event definitions (current count = 15)
EVENT_2x2       = Event("2x2", scrambler222.get_WCA_scramble, 5, True)
EVENT_3x3       = Event("3x3", scrambler333.get_WCA_scramble, 5, True)
EVENT_4x4       = Event("4x4", scrambler444.get_WCA_scramble, 5, True)
EVENT_5x5       = Event("5x5", scrambler555.get_WCA_scramble, 5, True)
EVENT_6x6       = Event("6x6", scrambler666.get_WCA_scramble, 3, True)
EVENT_7x7       = Event("7x7", scrambler777.get_WCA_scramble, 3, True)
EVENT_3BLD      = Event("3BLD", scrambler333.get_3BLD_scramble, 3, True)
EVENT_3x3OH     = Event("3x3OH", scrambler333.get_WCA_scramble, 5, True)
EVENT_Square1   = Event("Square-1", squareOneScrambler.get_WCA_scramble, 5, True)
EVENT_Pyraminx  = Event("Pyraminx", pyraminxScrambler.get_WCA_scramble, 5, True)
EVENT_Megaminx  = Event("Megaminx", megaminxScrambler.get_WCA_scramble, 5, True)
EVENT_Skewb     = Event("Skewb", skewbScrambler.get_WCA_scramble, 5, True)
EVENT_Clock     = Event("Clock", clockScrambler.get_WCA_scramble, 5, True)
EVENT_3x3_Feet  = Event("3x3 With Feet", scrambler333.get_WCA_scramble, 5, True)
EVENT_FMC       = Event("FMC", scrambler333.get_WCA_scramble, 5, True)

# non-WCA event definitions (current count = 14)
EVENT_2GEN      = Event("2GEN", scrambler333.get_2genRU_scramble, 5, False)
EVENT_LSE       = Event("LSE", scrambler333.get_2genMU_scramble, 5, False)
EVENT_COLL      = Event("COLL", COLL_scrambler, 5, False)
EVENT_F2L       = Event("F2L", scrambler333.get_WCA_scramble, 5, False)
EVENT_Void      = Event("Void Cube", scrambler333.get_3BLD_scramble, 5, False)
EVENT_Mirror    = Event("3x3 Mirror Blocks/Bump", scrambler333.get_WCA_scramble, 5, False)
EVENT_Kilominx  = Event("Kilominx", megaminxScrambler.get_WCA_scramble, 5, False)
EVENT_4x4OH     = Event("4x4 OH", scrambler444.get_WCA_scramble, 5, False)
EVENT_3x3x2     = Event("3x3x2", cuboidsScrambler.get_3x3x2_scramble, 5, False)
EVENT_3x3x4     = Event("3x3x4", cuboidsScrambler.get_3x3x4_scramble, 5, False)
EVENT_3x3x5     = Event("3x3x4", cuboidsScrambler.get_3x3x5_scramble, 5, False)
EVENT_234Relay  = Event("2-3-4 Relay", scrambler_234_relay, 3, False, scramble_generator=True)
EVENT_333Relay  = Event("3x3 Relay of 3", scrambler_333_relay, 3, False, scramble_generator=True)
EVENT_PLLAttack = Event("PLL Time Attack", lambda: 'Do all the PLLs!', 1, False)

# -------------------------------------------------------------------------------------------------

# Important! Only add new events all the way at the end, regardless of WCA or non-WCA status
# We rely on the order here
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
    EVENT_3x3x4,
    EVENT_Kilominx,
    EVENT_4x4OH,
    EVENT_LSE,
    EVENT_3x3x5,
    EVENT_234Relay,
    EVENT_PLLAttack,
]

# Important! Don't change how these WCA and non-WCA lists are built, we rely on the order
__WCA_EVENTS = [event for event in __ALL_EVENTS if event.is_wca]
__NON_WCA_EVENTS = [event for event in __ALL_EVENTS if not event.is_wca]

# Important! Don't change the order of these
__COLL_LIST = [
    'B1', 'B2', 'B3', 'B4', 'B5', 'B6',
    'C1', 'C2', 'C3', 'C4', 'C5', 'C6',
    'D1', 'D2', 'D3', 'D4', 'D5', 'D6',
    'E1', 'E2', 'E3', 'E4', 'E5', 'E6',
    'F1', 'F2', 'F3', 'F4', 'F5', 'F6',
    'G1', 'G2', 'G3', 'G4', 'G5', 'G6',
    'H1', 'H2', 'H3', 'H4'
]

# -------------------------------------------------------------------------------------------------

def get_num_COLLs():
    """ Returns the length of the COLLs list. """
    return len(__COLL_LIST)


def get_num_bonus_events():
    """ Returns the length of the bonus events list. """
    return len(__NON_WCA_EVENTS)


def get_WCA_events():
    """ Return all the WCA events. """
    return __WCA_EVENTS


def get_non_WCA_events():
    """ Return all the non-WCA events. """
    return __NON_WCA_EVENTS


def get_bonus_events_rotation_starting_at(starting_index, count=5):
    """ Gets a list of `count` non-WCA events starting at the specified index. """
    return __NON_WCA_EVENTS[starting_index : starting_index + count]


def get_bonus_events_without_current(bonus_events):
    """ Gets a list of the bonus events except for the current ones. """
    return [e for e in __NON_WCA_EVENTS if e not in bonus_events]


def get_COLL_at_index(index):
    """ Gets the COLL at the specified index. """
    return __COLL_LIST[index]
