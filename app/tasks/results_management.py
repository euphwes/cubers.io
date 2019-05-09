""" Tasks related to creating and scoring competitions. """

from app import app
from app.persistence.user_results_manager import get_all_complete_user_results_for_comp_and_user,\
    bulk_save_event_results

from . import huey

# -------------------------------------------------------------------------------------------------

__LOG_RETRO_BLACKLIST = 'retroactively blacklisted {results_count} user event results'

# -------------------------------------------------------------------------------------------------

@huey.task()
def blacklist_all_complete_results_for_user_and_comp(user_id: int, comp_id: int, username: str) -> None:
    """ A task to blacklist all as-of-yet-unblacklisted results for the specified user and competition. """

    results_to_save_in_bulk = list()

    for results in get_all_complete_user_results_for_comp_and_user(comp_id, user_id, include_blacklisted=False):
        results.is_blacklisted = True
        results.blacklist_note = 'Retroactively blacklisted due to user being flagged for weekly blacklist'
        results_to_save_in_bulk.append(results)

    bulk_save_event_results(results_to_save_in_bulk)
    app.logger.info(__LOG_RETRO_BLACKLIST.format(results_count=len(results_to_save_in_bulk)), extra={
        'comp_id': comp_id,
        'user_id': user_id,
        'username': username
    })
