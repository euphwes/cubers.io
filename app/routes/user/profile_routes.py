""" Routes related to a user's profile. """

from flask import render_template, redirect, url_for
from flask_login import current_user

from app import app
from app.business.user_history import get_user_competition_history
from app.persistence.comp_manager import get_user_participated_competitions_count
from app.persistence.user_manager import get_user_by_username, verify_user, unverify_user,\
    set_perma_blacklist_for_user, unset_perma_blacklist_for_user, get_user_by_id
from app.persistence.user_results_manager import get_user_completed_solves_count,\
    get_user_medals_count
from app.persistence.events_manager import get_events_id_name_mapping
from app.persistence.user_site_rankings_manager import get_site_rankings_for_user

# -------------------------------------------------------------------------------------------------

LOG_NO_SUCH_USER = "Oops, can't find a user with username '{}'"
LOG_PROFILE_VIEW = "{} is viewing {}'s profile"

# -------------------------------------------------------------------------------------------------

@app.route('/u/<username>/')
def profile(username):
    """ A route for showing a user's profile. """

    user = get_user_by_username(username)
    if not user:
        no_user_msg = LOG_NO_SUCH_USER.format(username)
        app.logger.warning(no_user_msg)
        return (no_user_msg, 404)

    # Determine whether we're showing blacklisted results
    include_blacklisted = __should_show_blacklisted_results(username, current_user.is_admin)

    app.logger.info(LOG_PROFILE_VIEW.format(current_user.username, username),
                    extra=__create_profile_view_log_context(current_user.is_admin, include_blacklisted))

    # Get the user's competition history
    history = get_user_competition_history(user, include_blacklisted=include_blacklisted)

    # Accumulate a count of medals this user has for podiuming
    gold_count, silver_count, bronze_count = get_user_medals_count(user.id)

    # Get some other interesting stats
    solve_count = get_user_completed_solves_count(user.id)
    comps_count = get_user_participated_competitions_count(user.id)

    # Get a dictionary of event ID to names, to facilitate rendering some stuff in the template
    event_id_name_map = get_events_id_name_mapping()

    # See if the user has any recorded site rankings. If they do, extract the data as a dict so we
    # can build their site ranking table
    site_rankings_record = get_site_rankings_for_user(user.id)
    if site_rankings_record:
        site_rankings = site_rankings_record.get_site_rankings_and_pbs(event_id_name_map)

        # Get sum of ranks
        sor_all     = site_rankings_record.get_combined_sum_of_ranks()
        sor_wca     = site_rankings_record.get_WCA_sum_of_ranks()
        sor_non_wca = site_rankings_record.get_non_WCA_sum_of_ranks()

        # Get Kinchranks
        kinch_all     = site_rankings_record.get_combined_kinchrank()
        kinch_wca     = site_rankings_record.get_WCA_kinchrank()
        kinch_non_wca = site_rankings_record.get_non_WCA_kinchrank()

        # If it exists, get the timestamp formatted like "2019 Jan 11"
        if site_rankings_record.timestamp:
            rankings_ts = site_rankings_record.timestamp.strftime('%Y %b %d')

        # If there is no timestamp, just say that the rankings as accurate as of the last comp
        # This should only happen briefly after I add the timestamp to the rankings table,
        # but before the rankings are re-calculated
        else:
            rankings_ts = "last competition-ish"

    else:
        rankings_ts   = None
        site_rankings = None
        sor_all       = None
        sor_wca       = None
        sor_non_wca   = None
        kinch_all     = None
        kinch_wca     = None
        kinch_non_wca = None

    # Set a flag indicating if this page view is for a user viewing another user's page
    viewing_other_user = user.username != current_user.username

    return render_template("user/profile.html", user=user, solve_count=solve_count,
        comp_count=comps_count, history=history, rankings=site_rankings,
        event_id_name_map=event_id_name_map, rankings_ts=rankings_ts,
        is_admin_viewing=current_user.is_admin, sor_all=sor_all, sor_wca=sor_wca,
        sor_non_wca=sor_non_wca, gold_count=gold_count, silver_count=silver_count,
        bronze_count=bronze_count, viewing_other_user=viewing_other_user,
        kinch_all=kinch_all, kinch_wca=kinch_wca, kinch_non_wca=kinch_non_wca)

# -------------------------------------------------------------------------------------------------

@app.route('/blacklist_user/<int:user_id>/')
def blacklist_user(user_id: int):
    """ Sets the perma-blacklist flag for the specified user. """

    if not (current_user.is_authenticated and (current_user.is_admin or current_user.is_results_moderator)):
        return ("Hey, you're not allowed to do that.", 403)

    set_perma_blacklist_for_user(user_id)

    user = get_user_by_id(user_id)
    if not user:
        return redirect(url_for('index'))

    return redirect(url_for('profile', username=user.username))


@app.route('/unblacklist_user/<int:user_id>/')
def unblacklist_user(user_id: int):
    """ Unsets the perma-blacklist flag for the specified user. """

    if not (current_user.is_authenticated and (current_user.is_admin or current_user.is_results_moderator)):
        return ("Hey, you're not allowed to do that.", 403)

    unset_perma_blacklist_for_user(user_id)

    user = get_user_by_id(user_id)
    if not user:
        return redirect(url_for('index'))

    return redirect(url_for('profile', username=user.username))


@app.route('/verify_user/<int:user_id>/')
def do_verify_user(user_id: int):
    """ Sets the verified flag for the specified user. """

    if not (current_user.is_authenticated and (current_user.is_admin or current_user.is_results_moderator)):
        return ("Hey, you're not allowed to do that.", 403)

    verify_user(user_id)

    user = get_user_by_id(user_id)
    if not user:
        return redirect(url_for('index'))

    return redirect(url_for('profile', username=user.username))


@app.route('/unverify_user/<int:user_id>/')
def do_unverify_user(user_id: int):
    """ Unsets the verified flag for the specified user. """

    if not (current_user.is_authenticated and (current_user.is_admin or current_user.is_results_moderator)):
        return ("Hey, you're not allowed to do that.", 403)

    unverify_user(user_id)

    user = get_user_by_id(user_id)
    if not user:
        return redirect(url_for('index'))

    return redirect(url_for('profile', username=user.username))

# -------------------------------------------------------------------------------------------------

def __should_show_blacklisted_results(profile_username, is_admin_here):
    """ Determine if we want to show blacklisted results in the competition history. """

    # If the user viewing a page is an admin, they can see blacklisted results
    if is_admin_here:
        return True

    # Non-logged-in users can't see blacklisted results
    if not current_user:
        return False

    # Users can see their own blacklisted results
    if current_user.username == profile_username:
        return True

    # Everybody else can't see blacklisted results
    return False


def __create_profile_view_log_context(show_admin, include_blacklisted):
    """ Builds some logging context related to viewing user profiles. """

    return {
        'is_admin': show_admin,
        'include_blacklisted_results': include_blacklisted
    }
