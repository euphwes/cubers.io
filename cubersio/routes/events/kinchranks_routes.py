""" Routes related to displaying overall Kinchranks results. """

from http import HTTPStatus

from flask import render_template

from cubersio import app
from cubersio.persistence.user_site_rankings_manager import get_user_kinchranks_all_sorted,\
    get_user_kinchranks_wca_sorted, get_user_kinchranks_non_wca_sorted

# -------------------------------------------------------------------------------------------------

__KINCH_TYPE_ALL     = 'all'
__KINCH_TYPE_WCA     = 'wca'
__KINCH_TYPE_NON_WCA = 'non_wca'
__VALID_KINCH_TYPES = (__KINCH_TYPE_ALL, __KINCH_TYPE_WCA, __KINCH_TYPE_NON_WCA)

__TITLE_MAP = {
    __KINCH_TYPE_ALL:     'Kinchranks – Combined',
    __KINCH_TYPE_WCA:     'Kinchranks – WCA',
    __KINCH_TYPE_NON_WCA: 'Kinchranks – Non-WCA',
}

__RESULTS_RETRIEVER_MAP = {
    __KINCH_TYPE_ALL:     get_user_kinchranks_all_sorted,
    __KINCH_TYPE_WCA:     get_user_kinchranks_wca_sorted,
    __KINCH_TYPE_NON_WCA: get_user_kinchranks_non_wca_sorted,
}

__INVALID_KINCH_TYPE = "\"{}\" isn't a valid Kinchranks type."

# -------------------------------------------------------------------------------------------------

@app.route('/kinchranks/<rank_type>/')
def kinchranks(rank_type):
    """ A route for showing Kinchranks. """

    if rank_type not in __VALID_KINCH_TYPES:
        err_msg = __INVALID_KINCH_TYPE.format(rank_type)
        return render_template('error.html', error_message=err_msg), HTTPStatus.NOT_FOUND

    sorted_kinchranks = __RESULTS_RETRIEVER_MAP[rank_type]()
    formatted_kinchranks = [(format(kr[0], '.3f'), kr[1]) for kr in sorted_kinchranks]

    return render_template("records/kinchranks.html", alternative_title="Kinchranks",
                            title=__TITLE_MAP[rank_type], sorted_kinchranks=formatted_kinchranks)
