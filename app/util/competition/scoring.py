""" Business logic for reading comments in a competition's Reddit thread, parsing submissions,
scoring users, and posting the results. """

from app import app
from app.persistence.comp_manager import get_competition, save_competition
from app.persistence.user_results_manager import get_all_complete_user_results_for_comp_event
from app.util.reddit import submit_post, update_post
from app.util.sorting import sort_user_event_results
from app.util.times import convert_centiseconds_to_friendly_time, convert_fmc_centimoves_to_moves

# -------------------------------------------------------------------------------------------------

__USER_PER_EVENT_LIMIT = 10
__USER_LIMIT_IN_POINTS = 50

__RESULTS_TITLE_TEMPLATE = 'Results for {comp_title}'
__RESULTS_EVENT_HEADER_TEMPLATE = '\n\n---\n\n**{event_name}**\n\n'
__RESULTS_USER_LINE_TEMPLATE = '1. {username}: {result}\n\n'
__RESULTS_USER_POINTS_TEMPLATE = '1. {username}: {points}\n\n'

__RESULTS_BODY_START_TEMPLATE = """
Thanks for checking out the results for [{comp_title}]({leaderboards_url})!

This results thread displays the top {event_user_limit} participants in each event,
as well as the top {point_user_limit} overall points earners.

As always, full results are available at [cubers.io](https://www.cubers.io) in the
[competition leaderboards section]({leaderboards_url})!

"""

__RESULTS_POINTS_SECTION_HEADER = '\n\n---\n\n**Total points this week**'
__RESULTS_POINTS_SECTION_HEADER += '\n\nEach event gives `# of participants - place + 1` points\n\n'

__LEADERBOARDS_URL_TEMPLATE = app.config['APP_URL'] + 'leaderboards/{comp_id}/'

__FMC = 'FMC'

# -------------------------------------------------------------------------------------------------

def post_results_thread(competition_id, is_rerun=False):
    """ Iterate over the events in the competition being scored """

    user_points = dict()

    # Retrieve the competition being scored
    comp = get_competition(competition_id)

    title = __RESULTS_TITLE_TEMPLATE.format(comp_title=comp.title)
    post_body = __RESULTS_BODY_START_TEMPLATE.format(comp_title=comp.title, point_user_limit=__USER_LIMIT_IN_POINTS,
        event_user_limit=__USER_PER_EVENT_LIMIT, leaderboards_url=__LEADERBOARDS_URL_TEMPLATE.format(comp_id=comp.id))

    # Iterate over all the events in the competition, simultaneously building up the post body and
    # tallying user points
    for comp_event in comp.events:
        results = list(get_all_complete_user_results_for_comp_event(comp_event.id))
        if not results:
            continue

        results.sort(key=sort_user_event_results)

        post_body += __RESULTS_EVENT_HEADER_TEMPLATE.format(event_name=comp_event.Event.name)

        total_participants = len(results)
        for i, result in enumerate(results):
            username = result.User.username
            if username not in user_points.keys():
                user_points[username] = 0
            user_points[username] += (total_participants - i)

            if i < __USER_PER_EVENT_LIMIT:
                if result.CompetitionEvent.Event.name == __FMC:
                    time = convert_fmc_centimoves_to_moves(result.result)
                else:
                    time = convert_centiseconds_to_friendly_time(result.result)
                post_body += __RESULTS_USER_LINE_TEMPLATE.format(username=username, result=time)

    user_points = [(username, points) for username, points in user_points.items()]
    user_points.sort(key=lambda x: x[1], reverse=True)

    post_body += __RESULTS_POINTS_SECTION_HEADER
    for username, points in user_points[:__USER_LIMIT_IN_POINTS]:
        post_body += __RESULTS_USER_POINTS_TEMPLATE.format(username=username, points=points)

    if not is_rerun:
        new_post_id = submit_post(title, post_body)
        comp.result_thread_id = new_post_id
        save_competition(comp)
    else:
        results_thread_id = comp.result_thread_id
        update_post(post_body, results_thread_id)
