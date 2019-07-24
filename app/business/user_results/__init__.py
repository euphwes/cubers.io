""" A package for creating and managing user event results. """

from app.persistence.user_results_manager import bulk_save_event_results, get_results_for_comp_event
from app.util.sorting import sort_user_results_with_rankings

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

        # Handle the case where nobody participated in an event. The Ranking(...) mechanism used
        # in sort_user_results_with_rankings chokes on empty iterables.
        if not unblacklisted_results:
            print('Skipping {}, no results to process'.format(comp_event.Event.name))
            continue

        results_with_rankings = sort_user_results_with_rankings(unblacklisted_results, comp_event.Event.eventFormat)
        print('Processed {} with {} total results'.format(comp_event.Event.name, len(results_with_rankings)))

        # Since identically-ranked results get the same podium (if they get a podium), it may be
        # that the silver and bronze raw rankings aren't "2" and "3". If there are 3 users with a
        # gold podium, then silver will be 4 and bronze will be 5, and so on.
        raw_available_ranks = set(r for r, _, _ in results_with_rankings)
        ranking_thresholds = sorted(list(raw_available_ranks))[:3]
        gold_rank   = ranking_thresholds[0] if len(ranking_thresholds) > 0 else -1
        silver_rank = ranking_thresholds[1] if len(ranking_thresholds) > 1 else -1
        bronze_rank = ranking_thresholds[2] if len(ranking_thresholds) > 2 else -1

        # Apply medals based on rankings
        for ranking, _, result in results_with_rankings:
            result.was_gold_medal   = (ranking == gold_rank) and result.result != 'DNF'
            result.was_silver_medal = (ranking == silver_rank) and result.result != 'DNF'
            result.was_bronze_medal = (ranking == bronze_rank) and result.result != 'DNF'

        # Save all event results with their updated medal flags
        bulk_save_event_results(results)
