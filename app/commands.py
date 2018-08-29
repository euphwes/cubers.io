""" Utility Flask commands for testing the app. """
#pylint: disable=C0103

import uuid, random

import click

from pyTwistyScrambler import scrambler222, scrambler333, scrambler444, scrambler555,\
     scrambler666, scrambler777, megaminxScrambler, skewbScrambler, squareOneScrambler,\
     pyraminxScrambler, clockScrambler, cuboidsScrambler

from . import CUBERS_APP
from .persistence.comp_manager import get_event_by_name, create_new_competition

# -------------------------------------------------------------------------------------------------

def get_2_3_4_relay_scramble():
    s2 = scrambler222.get_WCA_scramble()
    s3 = scrambler333.get_WCA_scramble()
    s4 = scrambler444.get_WCA_scramble()
    return "2x2: {}\n3x3: {}\n4x4: {}".format(s2, s3, s4)

def get_3_relay_of_3():
    scrambles = [scrambler333.get_WCA_scramble() for i in range(3)]
    return "1. {}\n 2. {}\n3. {}".format(*scrambles)

def get_COLL_scramble():
    return "COLL E" + str(random.choice(range(1,15)))

EVENTS_HELPER = {
    "3x3":             scrambler333.get_WCA_scramble,
    "2x2":             scrambler222.get_WCA_scramble,
    "4x4":             scrambler444.get_WCA_scramble,
    "5x5":             scrambler555.get_WCA_scramble,
    "6x6":             scrambler666.get_WCA_scramble,
    "7x7":             scrambler777.get_WCA_scramble,
    "3BLD":            scrambler333.get_3BLD_scramble,
    "Square-1":        squareOneScrambler.get_WCA_scramble,
    "Clock":           clockScrambler.get_WCA_scramble,
    "3x3OH":           scrambler333.get_WCA_scramble,
    "Pyraminx":        pyraminxScrambler.get_WCA_scramble,
    "Megaminx":        megaminxScrambler.get_WCA_scramble,
    "Kilominx":        megaminxScrambler.get_WCA_scramble,
    "Skewb":           skewbScrambler.get_WCA_scramble,
    "2GEN":            scrambler333.get_2genRU_scramble,
    "F2L":             scrambler333.get_WCA_scramble,
    "LSE":             scrambler333.get_2genMU_scramble,
    "COLL":            get_COLL_scramble,
    "4x4 OH":          scrambler444.get_WCA_scramble,
    "3x3x4":           cuboidsScrambler.get_3x3x4_scramble,
    "3x3x5":           cuboidsScrambler.get_3x3x5_scramble,
    "3x3x2":           cuboidsScrambler.get_3x3x2_scramble,
    "Void Cube":       scrambler333.get_3BLD_scramble,
    "2-3-4 Relay":     get_2_3_4_relay_scramble,
    "FMC":             scrambler333.get_WCA_scramble,
    "3x3 With Feet":   scrambler333.get_WCA_scramble,
    "3x3 Relay of 3":  get_3_relay_of_3,
    "PLL Time Attack": lambda: "Just do every PLL",
    "3x3 Mirror Blocks/Bump": scrambler333.get_WCA_scramble,
}

@CUBERS_APP.cli.command()
@click.option('--title', '-t', type=str)
@click.option('--reddit_id', '-r', type=str, default='')
def create_new_test_comp(title, reddit_id):
    """ Creates a new dummy competition for testing purposes. """

    event_data = []
    for event_name, scrambler in EVENTS_HELPER.items():
        data = dict()
        num_solves = get_event_by_name(event_name).totalSolves
        data['scrambles'] = [scrambler() for _ in range(num_solves)]
        data['name'] = event_name
        event_data.append(data)

    if not reddit_id:
        reddit_id = str(uuid.uuid4()).replace('-','')[:10]

    create_new_competition(title, reddit_id, event_data)
