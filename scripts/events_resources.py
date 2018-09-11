""" Resources for data related to events. """

#pylint: disable=C0103

from pyTwistyScrambler import scrambler333, scrambler222, scrambler444, scrambler555,\
    scrambler666, scrambler777, squareOneScrambler, megaminxScrambler, pyraminxScrambler,\
    cuboidsScrambler, skewbScrambler, clockScrambler

import text_resources as txt

# -------------------------------------------------------------------------------------------------

class Event:
    """ Encapsulates everything we need to know about an event. """

    def __init__(self, name, scramble_func, num_scrambles, is_wca, has_explanation=False):
        self.name = name
        self.scramble_func = scramble_func
        self.num_scrambles = num_scrambles
        self.is_wca = is_wca
        self.has_explanation = has_explanation

# -------------------------------------------------------------------------------------------------

# WCA event definitions
EVENT_2x2       = Event("2x2", scrambler222.get_WCA_scramble, 5, True)
EVENT_3x3       = Event("3x3", scrambler333.get_WCA_scramble, 5, True)
EVENT_4x4       = Event("4x4", scrambler444.get_WCA_scramble, 5, True)
EVENT_5x5       = Event("5x5", scrambler555.get_WCA_scramble, 5, True)
EVENT_6x6       = Event("6x6", scrambler666.get_WCA_scramble, 3, True)
EVENT_7x7       = Event("7x7", scrambler777.get_WCA_scramble, 3, True)
EVENT_3BLD      = Event("3BLD", scrambler333.get_3BLD_scramble, 3, True)
EVENT_3x3OH     = Event("3x3 OH", scrambler333.get_WCA_scramble, 5, True)
EVENT_Square1   = Event("Square-1", squareOneScrambler.get_WCA_scramble, 5, True)
EVENT_Pyraminx  = Event("Pyraminx", pyraminxScrambler.get_WCA_scramble, 5, True)
EVENT_Megaminx  = Event("Megaminx", megaminxScrambler.get_WCA_scramble, 5, True)
EVENT_Skewb     = Event("Skewb", skewbScrambler.get_WCA_scramble, 5, True)
EVENT_Clock     = Event("Clock", clockScrambler.get_WCA_scramble, 5, True)
EVENT_3x3_Feet  = Event("3x3 With Feet", scrambler333.get_WCA_scramble, 5, True)
EVENT_FMC       = Event("FMC", scrambler333.get_WCA_scramble, 5, True)

# non-WCA event definitions
EVENT_2GEN      = Event("2GEN", scrambler333.get_2genRU_scramble, 5, False)
EVENT_LSE       = Event("LSE", scrambler333.get_2genMU_scramble, 5, False)
EVENT_COLL      = Event("COLL", lambda: 'TODO: func for COLL #', 5, False)
EVENT_F2L       = Event("F2L", scrambler333.get_WCA_scramble, 5, False)
EVENT_Void      = Event("Void Cube", scrambler333.get_3BLD_scramble, 5, False)
EVENT_Mirror    = Event("3x3 Mirror Blocks/Bump", scrambler333.get_WCA_scramble, 5, False)
EVENT_Kilominx  = Event("Kilominx", megaminxScrambler.get_WCA_scramble, 5, False)
EVENT_4x4OH     = Event("4x4 OH", scrambler444.get_WCA_scramble, 5, False)
EVENT_3x3x2     = Event("3x3x2", cuboidsScrambler.get_3x3x2_scramble, 5, False)
EVENT_3x3x4     = Event("3x3x4", cuboidsScrambler.get_3x3x4_scramble, 5, False)
EVENT_3x3x5     = Event("3x3x4", cuboidsScrambler.get_3x3x5_scramble, 5, False)
EVENT_234Relay  = Event("2-3-4 Relay",  lambda: 'TODO: func for 2-3-4 relay', 3, False)
EVENT_333Relay  = Event("3x3 Relay of 3",  lambda: 'TODO: func for 3-3-3 relay', 3, False)
EVENT_PLLAttack = Event("PLL Time Attack",  lambda: 'Do all the PLLs', 3, False)

# -------------------------------------------------------------------------------------------------

ALL_EVENTS = [
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
    EVENT_2GEN,
    EVENT_LSE,
    EVENT_COLL,
    EVENT_F2L,
    EVENT_Void,
    EVENT_Mirror,
    EVENT_Kilominx,
    EVENT_4x4OH,
    EVENT_3x3x2,
    EVENT_3x3x4,
    EVENT_3x3x5,
    EVENT_234Relay,
    EVENT_333Relay,
    EVENT_PLLAttack,
]

WCA_EVENTS = [event for event in ALL_EVENTS if event.is_wca]
NON_WCA_EVENTS = [event for event in ALL_EVENTS if not event.is_wca]