""" Utility routes. """

from flask import redirect

from app import app
from app.persistence.comp_manager import get_previous_competition
from app.util.reddit import get_permalink_for_thread_id

# -------------------------------------------------------------------------------------------------

@app.route("/results")
def prev_results():
    """ Redirects to the Reddit URL for the previous competition's results. """

    comp = get_previous_competition()
    comp_url = get_permalink_for_thread_id(comp.result_thread_id)

    return redirect(comp_url)
