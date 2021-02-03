""" Routes related to displaying competition results. """

import arrow

from http import HTTPStatus

from flask import request, Response
from flask_login import current_user

from cubersio import app
from cubersio.persistence.user_results_manager import get_all_user_results_for_user
from cubersio.routes import api_login_required

# -------------------------------------------------------------------------------------------------

class TwistyTimerResultsExporter:
    """ Exports a user's solves to a format that can be imported into TwistyTimer."""

    tt_csv_header     = 'Puzzle,Category,Time(millis),Date(millis),Scramble,Penalty,Comment\n'
    tt_csv_template   = '"{puzzle}";"{category}";"{time}";"{date}";"{scramble}";"{penalty}";""\n'
    filename_template = "{username}_twistytimer_export_{date}.txt"

    # Maps the cubers.io event name to a puzzle/category that will be recognized by TwistyTimer
    # Not all cubers.io events will be exported to TwistyTimer, since there's not really a
    # reasonable place to put them. For example, it makes sense to make Kilominx a category
    # of Megaminx, but what regular event would Redi Cube be a category of? What about relays? etc
    event_name_to_category_map = {
        # NxN
        '2x2': ['222', 'Normal'],
        '3x3': ['333', 'Normal'],
        '4x4': ['444', 'Normal'],
        '5x5': ['555', 'Normal'],
        '6x6': ['666', 'Normal'],
        '7x7': ['777', 'Normal'],

        # Other WCA events
        'Square-1': ['sq1', 'Normal'],
        'Clock':    ['clock', 'Normal'],
        'Pyraminx': ['pyra', 'Normal'],
        'Megaminx': ['mega', 'Normal'],
        'Skewb':    ['skewb', 'Normal'],

        # 3x3 variants
        '3BLD':                   ['333', '3BLD'],
        'LSE':                    ['333', 'LSE'],
        'F2L':                    ['333', 'F2L'],
        '2GEN':                   ['333', '2-GEN'],
        '3x3OH':                  ['333', 'OH'],
        'Void Cube':              ['333', 'Void Cube'],
        '3x3 With Feet':          ['333', 'With Feet'],
        '3x3 Mirror Blocks/Bump': ['333', 'Mirror Blocks'],

        # Other NxN variants
        '2BLD':     ['222', '2BLD'],
        '4BLD':     ['444', '4BLD'],
        '4x4 OH':   ['444', 'OH'],
        '5BLD':     ['555', '5BLD'],
        'Kilominx': ['mega', 'Kilominx']
    }


    def __init__(self, username, event_name_results_map):
        self.username = username
        self.event_name_results_map = event_name_results_map


    def get_filename(self):
        """ Returns the file name for the solves export. """

        return self.filename_template.format(
            username = self.username,
            date = arrow.utcnow().format('YYYY-MM-DD_HH-mm')
        )


    def generate_results(self):
        """ Returns a generator which yield TwistyTimer-flavor CSV lines containing the user's
        solve info. """

        def gen_results():
            """ Generator which yields the TwistyTimer CSV lines solve by solve. """

            # The CSV header line
            yield self.tt_csv_header

            for event_name, results_list in self.event_name_results_map.items():

                # Skip events which don't naturally map to a puzzle/category in TwistyTimer
                if event_name not in self.event_name_to_category_map.keys():
                    continue

                # Grab the TwistyTimer puzzle and category mapping for this event
                puzzle, category = self.event_name_to_category_map[event_name]

                for results in results_list:
                    # Grab the timestamp from each solve's associated competition, convert to millis
                    # A little messy, since we'll have a handful of solves with the same start time,
                    # but it's the best we can do since I didn't think to save actual timestamp with
                    # each solve... oops.
                    date = int(results.CompetitionEvent.Competition.start_timestamp.timestamp()) * 1000

                    for solve in results.solves:

                        # Extract scramble text for this solve
                        scramble = solve.Scramble.scramble

                        # Determine penalty flag (0 = no penalty, 1 = +2, 2 = DNF)
                        penalty = "0"  # default to no penalty
                        if solve.is_dnf:
                            penalty = "2"
                        elif solve.is_plus_two:
                            penalty = "1"

                        # Get solve time in millis -- skip the solve if there's no time for some reason
                        if not solve.time:
                            continue
                        time = solve.time * 10

                        # Yield the actual CSV line for this solve
                        yield self.tt_csv_template.format(
                            puzzle   = puzzle,
                            category = category,
                            time     = time,
                            date     = date,
                            scramble = scramble,
                            penalty  = penalty
                        )

        return gen_results()

# -------------------------------------------------------------------------------------------------

EXPORTER_TYPE_MAP = {
    'twisty_timer': TwistyTimerResultsExporter
}

@app.route('/api/export')
@api_login_required
def export():
    """ A route for exporting a user's results. """

    export_type = request.args.get('type')
    if export_type not in EXPORTER_TYPE_MAP.keys():
        return HTTPStatus.NOT_IMPLEMENTED

    event_name_results_map = dict()
    for result in get_all_user_results_for_user(current_user.id):
        event_name = result.CompetitionEvent.Event.name
        if event_name in event_name_results_map.keys():
            event_name_results_map[event_name].append(result)
        else:
            event_name_results_map[event_name] = [result]

    solves_exporter = TwistyTimerResultsExporter(current_user.username, event_name_results_map)
    filename = solves_exporter.get_filename()

    return Response(solves_exporter.generate_results(),
            mimetype = "text/plain",
            headers  = {"Content-Disposition": "attachment;filename={}".format(filename)})
