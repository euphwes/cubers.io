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

# -------------------------------------------------------------------------------------------------

# TODO: put the sum of ranks sorting stuff somewhere else

def sort_sum_of_ranks_by_single(val1, val2):
    return val1.single - val2.single

def sort_sum_of_ranks_by_average(val1, val2):
    return val1.average - val2.average

def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class comparator:
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return comparator
