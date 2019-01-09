""" Routes related to displaying competition results. """

from flask import render_template
from flask_login import current_user

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
        return ("oops", 404)

    # Determine whether we're showing blacklisted results
    include_blacklisted = should_show_blacklisted_results(username)

    # Get the user's competition history
    history = get_user_competition_history(user, include_blacklisted=include_blacklisted)

    # Get some other interesting stats
    solve_count = get_user_completed_solves_count(user.id)
    comps_count = get_user_participated_competitions_count(user.id)

    # Get a dictionary of event ID to names, to facilitate rendering some stuff in the template
    event_id_name_map = get_events_id_name_mapping()

    # See if the user has any recorded site rankings. If they do, extract the data as a dict so we
    # can build their site ranking table
    site_rankings_record = get_site_rankings_for_user(user.id)
    if site_rankings_record:
        site_rankings = site_rankings_record.get_site_rankings_data_as_dict()
        previous_comp = site_rankings_record.competition.title
    else:
        site_rankings = None
        previous_comp = None

    return render_template("user/profile.html", user=user, solve_count=solve_count,\
        comp_count=comps_count, history=history, rankings=site_rankings,\
        event_id_name_map=event_id_name_map, previous_comp=previous_comp)

# -------------------------------------------------------------------------------------------------

def should_show_blacklisted_results(profile_username):
    """ Determine if we want to show blacklisted results in the competition history. """

    # Non-logged-in users can't see blacklisted results
    if not current_user.is_authenticated:
        return False

    # Users can see their own blacklisted results
    if current_user.username == profile_username:
        return True

    # If the user viewing a page is an admin, they can see blacklisted results
    if get_user_by_username(current_user.username).is_admin:
        return True

    # Everybody else can't see blacklisted results
    return False
