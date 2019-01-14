""" Routes related to displaying overall Sum Of Ranks results. """

from flask import render_template

from app import CUBERS_APP
from app.persistence.user_site_rankings_manager import get_user_site_rankings_all_sorted_single,\
    get_user_site_rankings_all_sorted_average, get_user_site_rankings_wca_sorted_average,\
    get_user_site_rankings_wca_sorted_single, get_user_site_rankings_non_wca_sorted_average,\
    get_user_site_rankings_non_wca_sorted_single

# -------------------------------------------------------------------------------------------------

SOR_TYPE_ALL     = 'all'
SOR_TYPE_WCA     = 'wca'
SOR_TYPE_NON_WCA = 'non_wca'

# -------------------------------------------------------------------------------------------------

@CUBERS_APP.route('/sum_of_ranks/<sor_type>/')
def sum_of_ranks(sor_type):
    """ A route for showing sum of ranks. """

    if not sor_type in (SOR_TYPE_ALL, SOR_TYPE_WCA, SOR_TYPE_NON_WCA):
        return ("I don't know what kind of Sum of Ranks this is.", 404)

    singles  = get_user_site_rankings_all_sorted_single()
    averages = get_user_site_rankings_all_sorted_average()

    # If "all", get combined Sum of Ranks
    if sor_type == SOR_TYPE_ALL:
        title = "Sum of Ranks – Combined"
        singles  = get_user_site_rankings_all_sorted_single()
        averages = get_user_site_rankings_all_sorted_average()

    # If "wca", get WCA Sum of Ranks
    elif sor_type == SOR_TYPE_WCA:
        title = "Sum of Ranks – WCA"
        singles  = get_user_site_rankings_wca_sorted_single()
        averages = get_user_site_rankings_wca_sorted_average()

    # Otherwise must be "non_wca", so get non-WCA Sum of Ranks
    else:
        title = "Sum of Ranks – Non-WCA"
        singles  = get_user_site_rankings_non_wca_sorted_single()
        averages = get_user_site_rankings_non_wca_sorted_average()

    return render_template("records/sum_of_ranks.html", title=title,\
        alternative_title="Sum of Ranks", sor_sorted_by_single=singles,\
        sor_sorted_by_average=averages)
