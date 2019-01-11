""" Utility routes to redirect to the relevant Reddit threads for the current competition and
previous results. """

from flask import request, redirect, url_for, render_template
from flask_login import current_user, login_user, logout_user

from app import CUBERS_APP
from app.persistence.comp_manager import get_active_competition, get_previous_competition
from app.persistence.user_manager import get_user_by_username
from app.util.reddit_util import get_permalink_for_comp_thread

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route("/current")
def current_comp():
    """ Redirects to the Reddit URL for the current competition. """

    comp = get_active_competition()
    comp_url = get_permalink_for_comp_thread(comp.reddit_thread_id)

    return redirect(comp_url)


@CUBERS_APP.route("/results")
def prev_results():
    """ Redirects to the Reddit URL for the previous competition's results. """

    comp = get_previous_competition()
    comp_url = get_permalink_for_comp_thread(comp.result_thread_id)

    return redirect(comp_url)

# -------------------------------------------------------------------------------------------------

def is_admin_viewing():
    """ Returns whether or not it's an admin viewing the page. """

    # Non-logged-in users can't see blacklisted results
    if not current_user.is_authenticated:
        return False

    # If the user viewing a page is an admin, they can see blacklisted results
    if get_user_by_username(current_user.username).is_admin:
        return True
