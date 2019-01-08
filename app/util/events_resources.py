""" Resources for data related to events. """

#pylint: disable=C0103

from random import choice

from pyTwistyScrambler import scrambler333, scrambler222, scrambler444, scrambler555,\
    scrambler666, scrambler777, squareOneScrambler, megaminxScrambler, pyraminxScrambler,\
    cuboidsScrambler, skewbScrambler, clockScrambler

# -------------------------------------------------------------------------------------------------

class Event:
    """ Encapsulates everything we need to know about an event. """

    # pylint: disable=C0301
    def __init__(self, name, scramble_func, num_scrambles, is_weekly, has_explanation=False, scramble_generator=False):
        self.name = name
        self.scramble_func = scramble_func
        self.num_scrambles = num_scrambles
        self.is_weekly = is_weekly
        self.has_explanation = has_explanation
        self.scramble_generator = scramble_generator

    def get_scrambles(self, *args):
        """ Gets the scrambles for this event. """

        if self.scramble_generator:
            return [s for s in self.scramble_func(*args)]

        return [self.scramble_func(*args) for _ in range(self.num_scrambles)]

# -------------------------------------------------------------------------------------------------

def redi_scrambler():
    """ Returns a scramble for a Redi cube in MoYu notation. """

    scramble = list()
    possible_moves = [["R", "R'"],["L", "L'"]]

    for _ in range(7):
        i = choice([0, 1]) # start each chunk with either R-moves or L-moves at random
        for n in range(choice([3, 4, 5])): # either 3, 4, or 5 moves between each 'x'
            ix = (i + n) % 2 # alternate between R-moves and L-moves each time
            scramble.append(choice(possible_moves[ix]))
        scramble.append('x')

    return ' '.join(scramble)


def COLL_scrambler(coll_num):
    """ Get a 'scramble' for the current COLL, which just says which one we're doing. """

    return "This week we're doing COLL {}".format(coll_num)


def FMC_scrambler():
    """ Returns an FMC scramble, which is just a normal WCA scramble with R' U' F padding. """

    scramble = scrambler333.get_WCA_scramble().strip()
    while does_FMC_scramble_have_cancellations(scramble):
        scramble = scrambler333.get_WCA_scramble().strip()
    return "R' U' F {} R' U' F".format(scramble)


def does_FMC_scramble_have_cancellations(scramble):
    """ Returns whether the supplied scramble would have cancellations when padding with
    R' U' F at the beginning and end, as FMC regulations require. """

    scramble = scramble.split(' ') # turn it into a list of moves

    # check if there are any obvious cancellations: F touch F at the beginning,
    # or R touching R at the end
    first, last = scramble[0], scramble[-1]
    if first in ("F", "F2", "F'") or last in ("R", "R'", "R2"):
        return True

    # if there are no "obvious" cancellations, next check if there are less obvious ones like:
    # ex: [R' U' F] B F' <rest>   --> F B F', the F-moves cancel
    # ex: <rest> R' L' [R' U' F]  --> R' L R', the R-moves cancel

    # if the first move is a B, then the following move being an F would result in a cancellation
    if first in ("B", "B'", "B2"):
        # if the first or last move is a B or L respectively, it's possible the 2nd
        # or next-to-last moves form a cancellation with the padding
        if scramble[1] in ("F", "F2", "F'"):
            return True

    # if the last move is a L, then the preceding move being an R would result in a cancellation
    if last in ("L", "L'", "L2"):
        if scramble[-2] in ("R", "R'", "R2"):
            return True

    # no cancellations! woohoo, we can use this scramble
    return False


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

# Weekly event definitions (current count = 19)
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
EVENT_FMC       = Event("FMC", FMC_scrambler, 3, True)
EVENT_2GEN      = Event("2GEN", scrambler333.get_2genRU_scramble, 5, True)
EVENT_LSE       = Event("LSE", scrambler333.get_2genMU_scramble, 5, True)
EVENT_4BLD      = Event("4BLD", scrambler444.get_4BLD_scramble, 3, True)
EVENT_5BLD      = Event("5BLD", scrambler555.get_5BLD_scramble, 3, True)

# Bonus event definitions (current count = 12)
EVENT_COLL      = Event("COLL", COLL_scrambler, 5, False)
EVENT_F2L       = Event("F2L", scrambler333.get_WCA_scramble, 5, False)
EVENT_Void      = Event("Void Cube", scrambler333.get_3BLD_scramble, 5, False)
EVENT_Mirror    = Event("3x3 Mirror Blocks/Bump", scrambler333.get_WCA_scramble, 5, False)
EVENT_Kilominx  = Event("Kilominx", megaminxScrambler.get_WCA_scramble, 5, False)
EVENT_4x4OH     = Event("4x4 OH", scrambler444.get_WCA_scramble, 5, False)
EVENT_3x3x2     = Event("3x3x2", cuboidsScrambler.get_3x3x2_scramble, 5, False)
EVENT_3x3x4     = Event("3x3x4", cuboidsScrambler.get_3x3x4_scramble, 5, False)
EVENT_3x3x5     = Event("3x3x5", cuboidsScrambler.get_3x3x5_scramble, 5, False)
EVENT_234Relay  = Event("2-3-4 Relay", scrambler_234_relay, 3, False, scramble_generator=True)
EVENT_333Relay  = Event("3x3 Relay of 3", scrambler_333_relay, 3, False, scramble_generator=True)
EVENT_PLLAttack = Event("PLL Time Attack", lambda: 'Do all the PLLs!', 1, False)
EVENT_2BLD      = Event("2BLD", scrambler222.get_WCA_scramble, 3, False)
EVENT_REDI      = Event("Redi Cube", redi_scrambler, 5, False)

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
    EVENT_2BLD,
    EVENT_4BLD,
    EVENT_5BLD,
    EVENT_REDI
]

# Important! Don't change how these weekly and bonus lists are built, we rely on the order
__WEEKLY_EVENTS = [event for event in __ALL_EVENTS if event.is_weekly]
__BONUS_EVENTS = [event for event in __ALL_EVENTS if not event.is_weekly]

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

    return len(__BONUS_EVENTS)


def get_weekly_events():
    """ Return all the weekly events. """

    return __WEEKLY_EVENTS


def get_bonus_events():
    """ Return all the bonus events. """

    return __BONUS_EVENTS


def get_bonus_events_rotation_starting_at(starting_index, count=5):
    """ Gets a list of `count` bonus events starting at the specified index. Use a doubled list
    of bonus events as a 'trick' to wrap around to the beginning if the starting index and count
    bring us past the end of the list. """

    double_wide = __BONUS_EVENTS * 2
    return double_wide[starting_index : starting_index + count]


def get_bonus_events_without_current(bonus_events):
    """ Gets a list of the bonus events except for the current ones. """

    return [e for e in __BONUS_EVENTS if e not in bonus_events]


def get_COLL_at_index(index):
    """ Gets the COLL at the specified index. """

    return __COLL_LIST[index]
