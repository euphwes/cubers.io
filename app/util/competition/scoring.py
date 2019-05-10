""" Business logic for reading comments in a competition's Reddit thread, parsing submissions,
scoring users, and posting the results. """

from app.persistence.user_manager import get_username_id_map
from app.persistence.events_manager import get_events_name_id_mapping
from app.util.reddit import submit_post, update_post

# -------------------------------------------------------------------------------------------------

# It's actually 40k characters, but let's bump it back a smidge to have a little breathing room
MAX_REDDIT_THREAD_LENGTH = 39500

# -------------------------------------------------------------------------------------------------

def post_results_thread(competition_id, is_rerun=False):
    """ Score the previous competition and post the results. """

    # TODO post scored thread based on results from DB, update docstring above
    pass

# -------------------------------------------------------------------------------------------------
