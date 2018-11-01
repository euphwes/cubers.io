""" Routes related to authentication. """

from flask import request, redirect, url_for, render_template
from flask_login import current_user, login_user, logout_user

from app import CUBERS_APP
from app.persistence import comp_manager
from app.util import reddit_util

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route("/current")
def current_comp():
    """ Redirects to the Reddit URL for the current competition. """
    comp = comp_manager.get_active_competition()
    comp_url = reddit_util.get_permalink_for_comp_thread(comp.reddit_thread_id)

    return redirect(comp_url)


@CUBERS_APP.route("/results")
def prev_results():
    """ Redirects to the Reddit URL for the previous competition's results. """
    comp = comp_manager.get_previous_competition()
    comp_url = reddit_util.get_permalink_for_comp_thread(comp.result_thread_id)

    return redirect(comp_url)


@CUBERS_APP.route('/current_title')
def current_title():
    """ Returns the current competition's title in plain text. """
    return comp_manager.get_active_competition().title
