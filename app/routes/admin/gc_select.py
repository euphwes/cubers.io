""" A collection of admin endpoints for selection of winners for the SCS gift card. """

import random

from flask import render_template

from app import app
from app.persistence.comp_manager import get_complete_competitions, get_competition,\
    get_participants_in_competition

# -------------------------------------------------------------------------------------------------

@app.route("/admin/gc_select/")
def gc_select():
    """ Display a list of complete competitions. """

    return render_template("admin/gc_select/comp_list.html", comps=get_complete_competitions())


@app.route("/admin/gc_select/<int:comp_id>/")
def gc_select_user(comp_id):
    """ Grab a list of participating users for the specified competition, and choose one at
    random. """

    users = get_participants_in_competition(comp_id)
    if not users:
        winner = 'nobody'
    else:
        winner = random.choice(users)

    selected_comp = get_competition(comp_id)

    return render_template("admin/gc_select/user_list.html", users=users, winner=winner,\
        selected_comp=selected_comp)


@app.route("/admin/confirm_code/<confirm_code>/")
def gc_confirm_recipient(confirm_code):
    """ TODO """
    pass


@app.route("/admin/deny_code/<deny_code>/")
def gc_deny_recipient(deny_code):
    """ TODO """
    pass