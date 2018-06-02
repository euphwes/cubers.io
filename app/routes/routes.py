from app import CUBERS_APP
from app.persistence import comp_manager

from flask import render_template
from flask_login import current_user

import sys

@CUBERS_APP.route('/')
def index():
    """ Main page for the app. Shows the competition time entry page if logged in, or an informative
    landing page if not. """
    #if current_user.is_authenticated:
        #return render_template('comp.html')
    return render_template('index.html', current_competition = comp_manager.get_active_competition())



@CUBERS_APP.route('/comp/<competition_id>')
def competition(competition_id):
    try:
        competition_id = int(competition_id)
    except ValueError:
        print("Invalid competition_id", file=sys.stderr)
        
    return render_template('comp.html', competition = comp_manager.get_competition(competition_id))