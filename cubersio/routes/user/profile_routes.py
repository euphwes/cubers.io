""" Routes related to a user's profile. """

from http import HTTPStatus

from flask import render_template, redirect, url_for
from flask_login import current_user

from cubersio import app
from cubersio.business.user_history import get_user_competition_history
from cubersio.persistence.comp_manager import get_user_participated_competitions_count
from cubersio.persistence.events_manager import get_all_events
from cubersio.persistence.user_manager import verify_user, unverify_user,\
    set_perma_blacklist_for_user, unset_perma_blacklist_for_user, get_user_by_id,\
    get_user_by_username_case_insensitive
from cubersio.persistence.user_results_manager import get_user_completed_solves_count,\
    get_user_medals_count
from cubersio.persistence.user_site_rankings_manager import get_site_rankings_for_user
from cubersio.persistence.settings_manager import get_boolean_setting_for_user, SettingCode

# -------------------------------------------------------------------------------------------------

MSG_NO_SUCH_USER = "Oops, can't find a user with username '{}'"
TIMESTAMP_FORMAT = '%Y %b %d'

# -------------------------------------------------------------------------------------------------

@app.route('/u/<username>/')
def profile(username):
    """ A route for showing a user's profile. """

    user = get_user_by_username_case_insensitive(username)
    if not user:
        no_user_msg = MSG_NO_SUCH_USER.format(username)
        return render_template('error.html', error_message=no_user_msg), HTTPStatus.NOT_FOUND

    # Pull username from the user itself, so we know it's cased correctly for comparisons and
    # queries later
    username = user.username

    # Determine whether we're showing blacklisted results
    include_blacklisted = __should_show_blacklisted_results(username, current_user.is_admin)

    # Get the user's competition history
    history = get_user_competition_history(user, include_blacklisted=include_blacklisted)

    # Accumulate a count of medals this user has for podiuming
    gold_count, silver_count, bronze_count = get_user_medals_count(user.id)

    # Get some other interesting stats
    solve_count = get_user_completed_solves_count(user.id)
    comps_count = get_user_participated_competitions_count(user.id)

    # Get a dictionary of event ID to names, to facilitate rendering some stuff in the template
    event_id_name_map = {e.id: e.name for e in get_all_events()}

    # See if the user has any recorded site rankings. If they do, extract the data as a dict so we
    # can build their site ranking table
    site_rankings_record = get_site_rankings_for_user(user.id)
    if site_rankings_record:
        # TODO -- get the raw site rankings record back, sort those, then convert to dict for front-end
        site_rankings = site_rankings_record.get_site_rankings_and_pbs()

        # Get sum of ranks
        sor_all     = site_rankings_record.get_combined_sum_of_ranks()
        sor_wca     = site_rankings_record.get_WCA_sum_of_ranks()
        sor_non_wca = site_rankings_record.get_non_WCA_sum_of_ranks()

        # Get Kinchranks
        kinch_all     = site_rankings_record.get_combined_kinchrank()
        kinch_wca     = site_rankings_record.get_WCA_kinchrank()
        kinch_non_wca = site_rankings_record.get_non_WCA_kinchrank()

        # Timestamp of the last time site rankings were run, formatted like "2019 Jan 11"
        rankings_ts = site_rankings_record.timestamp.strftime(TIMESTAMP_FORMAT)

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
    viewing_self = user.username == current_user.username

    # Check if user has set WCA ID to be public
    show_wca_id = get_boolean_setting_for_user(user.id, SettingCode.SHOW_WCA_ID)

    # Set flags to indicate if user is missing a Reddit/WCA profile association
    missing_wca_association = viewing_self and username == user.reddit_id and not user.wca_id
    missing_reddit_association = viewing_self and username == user.wca_id and not user.reddit_id

    return render_template("user/profile.html", user=user, solve_count=solve_count,
                           comp_count=comps_count, history=history, rankings=site_rankings,
                           event_id_name_map=event_id_name_map, rankings_ts=rankings_ts,
                           is_admin_viewing=current_user.is_admin, sor_all=sor_all,
                           sor_wca=sor_wca, sor_non_wca=sor_non_wca, gold_count=gold_count,
                           silver_count=silver_count, bronze_count=bronze_count,
                           viewing_self=viewing_self, kinch_all=kinch_all, kinch_wca=kinch_wca,
                           kinch_non_wca=kinch_non_wca, show_wca_id=show_wca_id,
                           missing_wca_association=missing_wca_association,
                           missing_reddit_association=missing_reddit_association)

# -------------------------------------------------------------------------------------------------

@app.route('/blacklist_user/<int:user_id>/')
def blacklist_user(user_id: int):
    """ Sets the perma-blacklist flag for the specified user. """

    if not (current_user.is_authenticated and current_user.is_admin):
        return ("Hey, you're not allowed to do that.", 403)

    set_perma_blacklist_for_user(user_id)

    user = get_user_by_id(user_id)
    if not user:
        return redirect(url_for('index'))

    return redirect(url_for('profile', username=user.username))


@app.route('/unblacklist_user/<int:user_id>/')
def unblacklist_user(user_id: int):
    """ Unsets the perma-blacklist flag for the specified user. """

    if not (current_user.is_authenticated and current_user.is_admin):
        return ("Hey, you're not allowed to do that.", 403)

    unset_perma_blacklist_for_user(user_id)

    user = get_user_by_id(user_id)
    if not user:
        return redirect(url_for('index'))

    return redirect(url_for('profile', username=user.username))


@app.route('/verify_user/<int:user_id>/')
def do_verify_user(user_id: int):
    """ Sets the verified flag for the specified user. """

    if not (current_user.is_authenticated and current_user.is_admin):
        return ("Hey, you're not allowed to do that.", 403)

    verify_user(user_id)

    user = get_user_by_id(user_id)
    if not user:
        return redirect(url_for('index'))

    return redirect(url_for('profile', username=user.username))


@app.route('/unverify_user/<int:user_id>/')
def do_unverify_user(user_id: int):
    """ Unsets the verified flag for the specified user. """

    if not (current_user.is_authenticated and current_user.is_admin):
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
