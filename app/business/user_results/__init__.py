""" A package for creating and managing user event results. """

from app.persistence.user_results_manager import bulk_save_event_results, get_results_for_comp_event
from app.util.sorting import sort_user_event_results

# -------------------------------------------------------------------------------------------------

# A few constants which should be useful in multiple user results-related modules in this package
FMC = 'FMC'
DNF = 'DNF'
DNS = 'DNS'

# -------------------------------------------------------------------------------------------------
#              Stuff related to processing medals for top results in events
# -------------------------------------------------------------------------------------------------

def set_medals_on_best_event_results(comp_events):
    """ Iterates over a list of CompetitionEvents, gets the fastest 3 results for that event and
    sets the gold, silver, or bronze medal flags as appropriate. """

    for comp_event in comp_events:
        results = get_results_for_comp_event(comp_event.id)

        # Simultaneously pull out the unblacklisted results, and ensure that blacklisted
        # results do not have any medals set.
        unblacklisted_results = list()
        for result in results:
            if result.is_blacklisted:
                result.was_bronze_medal = False
                result.was_silver_medal = False
                result.was_gold_medal   = False
            else:
                unblacklisted_results.append(result)

        # Sort the unblacklisted results by their result value
        unblacklisted_results.sort(key=sort_user_event_results)

        # 1st is gold medal, 2nd is silver, 3rd is bronze, everything else has no medal
        for i, result in enumerate(unblacklisted_results):
            result.was_gold_medal   = (i == 0) and result.result != 'DNF'
            result.was_silver_medal = (i == 1) and result.result != 'DNF'
            result.was_bronze_medal = (i == 2) and result.result != 'DNF'

        # Save all event results with their updated medal flags
        bulk_save_event_results(results)
