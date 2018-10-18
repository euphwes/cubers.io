""" A collection of admin endpoints for selection of winners for the SCS gift card. """

from flask import request, redirect, url_for, render_template
import random

from app import CUBERS_APP
from app.persistence import comp_manager

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route("/admin/gc_select/")
def gc_select():
    """ Display a list of complete competitions. """
    comps = comp_manager.get_complete_competitions()
    comp = comp_manager.get_active_competition()

    return render_template("admin/gc_select/comp_list.html", comps=comps, current_competition=comp)


@CUBERS_APP.route("/admin/gc_select/<int:comp_id>/")
def gc_select_user(comp_id):
    """ Grab a list of participating users for the specified competition, and choose one at random. """

    users = comp_manager.get_participants_in_competition(comp_id)
    if not users:
        winner = 'nobody'
    else:
        winner = random.choice(users)

    comp = comp_manager.get_active_competition()
    selected_comp = comp_manager.get_competition(comp_id)

    return render_template("admin/gc_select/user_list.html", users=users, winner=winner, current_competition=comp,
        selected_comp=selected_comp)