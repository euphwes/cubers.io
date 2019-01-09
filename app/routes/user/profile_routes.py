""" Routes related to displaying competition results. """

from flask import render_template

from app import CUBERS_APP
from app.business.user_history import get_user_competition_history
from app.persistence.comp_manager import get_user_participated_competitions_count
from app.persistence.user_manager import get_user_by_username
from app.persistence.user_results_manager import get_user_completed_solves_count
from app.persistence.events_manager import get_events_id_name_mapping
from app.persistence.user_site_rankings_manager import get_site_rankings_for_user

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route('/u/<username>/')
def profile(username):
    """ A route for showing a user's profile. """

    user = get_user_by_username(username)
    if not user:
        return "oops"

    # TODO: BLACKLIST indicate blacklisted results in user's competition history table
    comp_history = get_user_competition_history(user)

    solve_count = get_user_completed_solves_count(user.id)
    comps_count = get_user_participated_competitions_count(user.id)

    event_id_name_map = get_events_id_name_mapping()
    site_rankings_record = get_site_rankings_for_user(user.id)
    if site_rankings_record:
        site_rankings = site_rankings_record.get_site_rankings_data_as_dict()
        previous_comp = site_rankings_record.competition.title
    else:
        site_rankings = None
        previous_comp = None

    return render_template("user/profile.html", user=user, solve_count=solve_count, comp_count=comps_count,\
        history=comp_history, rankings=site_rankings, event_id_name_map=event_id_name_map, previous_comp=previous_comp)
