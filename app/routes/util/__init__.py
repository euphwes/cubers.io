""" Utility routes to redirect to the relevant Reddit threads for the current competition and
previous results. """

from flask import redirect
from flask_login import current_user

from app import app
from app.persistence.comp_manager import get_active_competition, get_previous_competition
from app.util.reddit import get_permalink_for_comp_thread

# -------------------------------------------------------------------------------------------------

@app.route("/current")
def current_comp():
    """ Redirects to the Reddit URL for the current competition. """

    comp = get_active_competition()
    comp_url = get_permalink_for_comp_thread(comp.reddit_thread_id)

    return redirect(comp_url)


@app.route("/results")
def prev_results():
    """ Redirects to the Reddit URL for the previous competition's results. """

    comp = get_previous_competition()
    comp_url = get_permalink_for_comp_thread(comp.result_thread_id)

    return redirect(comp_url)

# -------------------------------------------------------------------------------------------------

def is_admin_viewing():
    """ Returns whether or not it's an admin viewing the page. """

    if not current_user.is_authenticated:
        return False

    return current_user.is_admin
