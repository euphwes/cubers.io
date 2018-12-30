""" Routes related to displaying competition results. """

from flask import render_template, redirect
from flask_login import current_user

from app import CUBERS_APP
from app.persistence.user_manager import get_user_by_username
from app.persistence.user_results_manager import get_user_competition_history,\
    get_user_completed_solves_count, get_user_participated_competitions_count

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route('/u/<username>/')
def profile(username):
    """ A route for showing a user's profile. """

    user = get_user_by_username(username)
    if not user:
        return "oops"

    comp_history = get_user_competition_history(user)

    solve_count = get_user_completed_solves_count(user.id)
    comps_count = get_user_participated_competitions_count(user.id)

    #site_rankings = get_pbs_and_site_rankings_for_user(user.id)
    site_rankings = dict()

    return render_template("user/profile.html", user=user, solve_count=solve_count, comp_count=comps_count,\
        history=comp_history, rankings=site_rankings)
