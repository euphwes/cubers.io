""" Utility Flask commands for testing the app. """
#pylint: disable=C0103

import uuid
from random import choice

import click
'''
try:
    from pyTwistyScrambler import scrambler222, scrambler333, scrambler444, scrambler555,\
        scrambler666, scrambler777, megaminxScrambler, skewbScrambler, squareOneScrambler

    scramble333 = scrambler333.get_WCA_scramble
    scramble222 = scrambler222.get_WCA_scramble
    scramble444 = scrambler444.get_WCA_scramble
    scramble555 = scrambler555.get_WCA_scramble
    scramble666 = scrambler666.get_WCA_scramble
    scramble777 = scrambler777.get_WCA_scramble
    scramble3bld = scrambler333.get_3BLD_scramble
    scrambleSkewb = skewbScrambler.get_WCA_scramble
    scrambleSq1 = squareOneScrambler.get_WCA_scramble
    scrambleMega = megaminxScrambler.get_WCA_scramble
'''
# I don't care to import the specific execJS "no JS runtime" exception for this
#pylint: disable=W0702
#except:
    # our environment could possibly not have a Javascript runtime, like Heroku
    # with Python buildpack apparently... default to a dummy scrambler function
dummy_scrambler = lambda: ' '.join(choice('RFLUDB') for _ in range(10))
scramble333 = dummy_scrambler
scramble222 = dummy_scrambler
scramble444 = dummy_scrambler
scramble555 = dummy_scrambler
scramble666 = dummy_scrambler
scramble777 = dummy_scrambler
scramble3bld = dummy_scrambler
scrambleSkewb = dummy_scrambler
scrambleSq1 = dummy_scrambler
scrambleMega = dummy_scrambler

from . import CUBERS_APP
from .persistence.comp_manager import get_event_by_name, create_new_competition

# -------------------------------------------------------------------------------------------------

EVENTS_HELPER = {
    "3x3":      scramble333,
    "2x2":      scramble222,
    "4x4":      scramble444,
    "5x5":      scramble555,
    "6x6":      scramble666,
    "7x7":      scramble777,
    "3BLD":     scramble333,
    "Skewb":    scrambleSkewb,
    "Square-1": scrambleSq1,
    "Megaminx": scrambleMega,
}

@CUBERS_APP.cli.command()
@click.argument("title")
def create_new_test_comp(title):
    """ Creates a new dummy competition for testing purposes. """

    event_data = []
    for event_name, scrambler in EVENTS_HELPER.items():
        data = dict()
        num_solves = get_event_by_name(event_name).totalSolves
        data['scrambles'] = [scrambler() for _ in range(num_solves)]
        data['name'] = event_name
        event_data.append(data)

    reddit_id = str(uuid.uuid4()).replace('-','')[:10]
    create_new_competition(title, reddit_id, event_data)
