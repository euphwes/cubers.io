""" Utility Flask commands for testing the app. """
#pylint: disable=C0103

import uuid
from random import choice

import click

from . import CUBERS_APP
from .persistence.comp_manager import get_event_by_name, create_new_competition

# -------------------------------------------------------------------------------------------------

DUMMY_SCRAMBLER = lambda: ' '.join(choice('RFLUDB') for _ in range(10))

EVENTS_LIST = ["3x3", "2x2", "4x4", "5x5", "6x6", "7x7", "3BLD", "Skewb", "Square-1", "Megaminx"]

@CUBERS_APP.cli.command()
@click.option('--title', '-t', type=str)
@click.option('--reddit_id', '-r', type=str, default='')
def create_new_test_comp(title, reddit_id):
    """ Creates a new dummy competition for testing purposes. """

    event_data = []
    for event_name in EVENTS_LIST:
        data = dict()
        num_solves = get_event_by_name(event_name).totalSolves
        data['scrambles'] = [DUMMY_SCRAMBLER() for _ in range(num_solves)]
        data['name'] = event_name
        event_data.append(data)

    if not reddit_id:
        reddit_id = str(uuid.uuid4()).replace('-','')[:10]

    create_new_competition(title, reddit_id, event_data)
