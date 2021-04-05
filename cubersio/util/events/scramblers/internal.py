""" Hand-written scramblers and scramble-related utility functions. """

from random import choice
from typing import List

from pyTwistyScrambler import scrambler333, scrambler222, scrambler444, ftoScrambler

from cubersio import app
from .sliding_tile import get_random_moves_scramble, get_random_state_scramble


def mbld_scrambler() -> str:
    """ Returns a 'scramble' for MBLD. """

    scramble = 'Scramble as many 3x3s as needed for your MBLD attempt.'
    scramble += '\nPlease limit your attempt to 60 minutes,'
    scramble += '\nand account for +2s manually.'
    scramble += '\nWe will be providing scrambles soon.'
    return scramble


def attack_scrambler() -> str:
    """ Returns a 'scramble' for PLL Time Attack. """

    scramble = 'Do all the PLLs!'
    scramble += "\nOrder doesn't matter, and the cube"
    scramble += "\ndoesn't need to be solved when finished."

    return scramble


def redi_scrambler(total_faces: int = 7) -> str:
    """ Returns a scramble for a Redi cube in MoYu notation. """

    scramble = list()
    possible_moves = [["R", "R'"], ["L", "L'"]]

    for _ in range(total_faces):
        i = choice([0, 1])  # start each chunk with either R-moves or L-moves at random
        for n in range(choice([3, 4, 5])):  # either 3, 4, or 5 moves between each 'x'
            ix = (i + n) % 2  # alternate between R-moves and L-moves each time
            scramble.append(choice(possible_moves[ix]))
        scramble.append('x')

    return ' '.join(scramble)


def fifteen_puzzle_scrambler() -> str:
    """ Returns a scramble for a 15 Puzzle.

    15 Puzzle is a sliding tile puzzle that looks like this when solved:

    [ 1] [ 2] [ 3] [ 4]
    [ 5] [ 6] [ 7] [ 8]
    [ 9] [10] [11] [12]
    [13] [14] [15] [  ]

    The bottom-right corner is empty, and it's with respect to the current position of the empty space that we move
    other pieces.

    U = up, which indicates the tile below the empty space moves up into the space
    D = down, which indicates the tile above the empty space moves down into the space
    R = right, which indicates the tile to the left of the empty space moves right into the space
    L = left, which indicates the tile to the right of the empty space moves left into the space
    """

    if app.config['IS_DEVO']:
        return get_random_moves_scramble(4)
    else:
        return get_random_state_scramble(4)


def fmc_scrambler() -> str:
    """ Returns an FMC scramble, which is just a normal WCA scramble with R' U' F padding. """

    scramble = scrambler333.get_WCA_scramble().strip()
    while does_fmc_scramble_have_cancellations(scramble):
        scramble = scrambler333.get_WCA_scramble().strip()
    return "R' U' F {} R' U' F".format(scramble)


def does_fmc_scramble_have_cancellations(scramble: str) -> bool:
    """ Returns whether the supplied scramble would have cancellations when padding with R' U' F at the beginning
    and end, as FMC regulations require. """

    # Turn it into a list of moves
    scramble = scramble.split(' ')

    # Check if there are any obvious cancellations: F touch F at the beginning, or R touching R at the end
    first, last = scramble[0], scramble[-1]
    if first in ("F", "F2", "F'") or last in ("R", "R'", "R2"):
        return True

    # If there are no "obvious" cancellations, next check if there are less obvious ones like:
    # ex: [R' U' F] B F' <rest>   --> F B F', the F-moves cancel
    # ex: <rest> R' L' [R' U' F]  --> R' L R', the R-moves cancel

    # If the first move is a B, then the following move being an F would result in a cancellation.
    if first in ("B", "B'", "B2"):
        # If the first or last move is a B or L respectively, it's possible the 2nd or next-to-last moves form a
        # cancellation with the padding
        if scramble[1] in ("F", "F2", "F'"):
            return True

    # If the last move is a L, then the preceding move being an R would result in a cancellation.
    if last in ("L", "L'", "L2"):
        if scramble[-2] in ("R", "R'", "R2"):
            return True

    # No cancellations! Woohoo, we can use this scramble.
    return False


def scrambler_234_relay() -> str:
    """ Get a scramble for the 2-3-4 relay event. """

    s222 = scrambler222.get_WCA_scramble()
    s333 = scrambler333.get_WCA_scramble()
    s444 = scrambler444.get_random_state_scramble()

    return f'2x2: {s222}\n3x3: {s333}\n4x4: {s444}'


def scrambler_333_relay() -> str:
    """ Get a scramble for the 3x3 relay of 3 event. """

    s1 = scrambler333.get_WCA_scramble()
    s2 = scrambler333.get_WCA_scramble()
    s3 = scrambler333.get_WCA_scramble()

    return f'1: {s1}\n2: {s2}\n3: {s3}'
