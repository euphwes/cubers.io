""" Routes related to the time-entry and competition results pages. """

from flask import render_template, abort

from app import CUBERS_APP
from app.persistence import comp_manager

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route('/')
def index():
    """ Main page for the app. Shows the competition time entry page if logged in, or an informative
    landing page if not. """
    competition = comp_manager.get_active_competition()
    return render_template('index.html', current_competition = competition)


@CUBERS_APP.route('/comp/<competition_id>')
def competition(competition_id):
    try:
        competition_id = int(competition_id)
    except ValueError:
        # TODO: come up with custom 404 not found page
        return abort(404)

    return render_template('comp.html', competition = comp_manager.get_competition(competition_id))
