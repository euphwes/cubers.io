""" Routes related to displaying overall Kinchranks results. """

from flask import render_template

from app import app
from app.persistence.user_site_rankings_manager import get_user_kinchranks_all_sorted,\
    get_user_kinchranks_wca_sorted, get_user_kinchranks_non_wca_sorted

# -------------------------------------------------------------------------------------------------

KINCH_TYPE_ALL     = 'all'
KINCH_TYPE_WCA     = 'wca'
KINCH_TYPE_NON_WCA = 'non_wca'

# -------------------------------------------------------------------------------------------------

@app.route('/kinchranks/<rank_type>/')
def kinchranks(rank_type):
    """ A route for showing Kinchranks. """

    if rank_type not in (KINCH_TYPE_ALL, KINCH_TYPE_WCA, KINCH_TYPE_NON_WCA):
        return ("I don't know what kind of Kinchranks this is.", 404)

    # If "all", get combined Kinchranks
    if rank_type == KINCH_TYPE_ALL:
        title = "Kinchranks – Combined"
        sorted_kinchranks = get_user_kinchranks_all_sorted()

    # If "wca", get WCA Kinchranks
    elif rank_type == KINCH_TYPE_WCA:
        title = "Kinchranks – WCA"
        sorted_kinchranks = get_user_kinchranks_wca_sorted()

    # Otherwise must be "non_wca", so get non-WCA Kinchranks
    else:
        title = "Kinchranks – Non-WCA"
        sorted_kinchranks = get_user_kinchranks_non_wca_sorted()

    sorted_kinchranks = [(format(kr[0], '.3f'), kr[1]) for kr in sorted_kinchranks]

    return render_template("records/kinchranks.html", title=title,
        alternative_title="Kinchranks", sorted_kinchranks=sorted_kinchranks)
