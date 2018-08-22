""" Utility Flask commands for testing the app. """
#pylint: disable=C0103

import uuid

import click

from pyTwistyScrambler import scrambler222, scrambler333, scrambler444, scrambler555,\
     scrambler666, scrambler777, megaminxScrambler, skewbScrambler, squareOneScrambler,\
     pyraminxScrambler

from . import CUBERS_APP
from .persistence.comp_manager import get_event_by_name, create_new_competition

# -------------------------------------------------------------------------------------------------

EVENTS_HELPER = {
    "3x3":      scrambler333.get_WCA_scramble,
    "2x2":      scrambler222.get_WCA_scramble,
    "4x4":      scrambler444.get_WCA_scramble,
    "5x5":      scrambler555.get_WCA_scramble,
    "6x6":      scrambler666.get_WCA_scramble,
    "7x7":      scrambler777.get_WCA_scramble,
    "3BLD":     scrambler333.get_3BLD_scramble,
    "Skewb":    skewbScrambler.get_WCA_scramble,
    "Square-1": squareOneScrambler.get_WCA_scramble,
    "Megaminx": megaminxScrambler.get_WCA_scramble,
    "Pyraminx": pyraminxScrambler.get_WCA_scramble,
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
