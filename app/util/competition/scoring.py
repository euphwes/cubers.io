""" Business logic for reading comments in a competition's Reddit thread, parsing submissions,
scoring users, and posting the results. """

from os import environ

from app import app
from app.persistence.comp_manager import get_competition, save_competition
from app.persistence.user_results_manager import get_all_complete_user_results_for_comp_event
from app.util.reddit import submit_post, update_post
from app.util.sorting import sort_user_results_with_rankings
from app.util.events.resources import sort_comp_events_by_global_sort_order

# -------------------------------------------------------------------------------------------------

__USER_PER_EVENT_LIMIT = 10
__USER_LIMIT_IN_POINTS = 50

__RESULTS_TITLE_TEMPLATE = 'Results for cubers.io weekly competition {comp_title}!'
__RESULTS_EVENT_HEADER_TEMPLATE = '\n\n---\n\n**{event_name}**\n\n'
__RESULTS_USER_LINE_TEMPLATE = '1. [{username}]({profile_url}): {result}\n\n'
__RESULTS_USER_POINTS_TEMPLATE = '1. [{username}]({profile_url}): {points}\n\n'

__RESULTS_BODY_START_TEMPLATE = """
Thanks for checking out the results for this week's [cubers.io](https://www.cubers.io) competition
 [{comp_title}]({leaderboards_url})!

For those who haven't yet joined in, come compete with us! [cubers.io](https://www.cubers.io) is a
website where you can participate in weekly WCA-style cubing competitions with fellow cubers from
around the world. You can log in with either your Reddit or your WCA account! To keep things
fresh, there is a rotating selection of non-WCA bonus events as well.

This results thread displays the top {event_user_limit} participants in each event,
as well as the top {point_user_limit} overall points earners.

As always, full results are available at [cubers.io](https://www.cubers.io) in the
[competition leaderboards section]({leaderboards_url})!

"""

__RESULTS_POINTS_SECTION_HEADER = '\n\n---\n\n**Total points this week**'
__RESULTS_POINTS_SECTION_HEADER += '\n\nEach event gives `# of participants - place + 1` points\n\n'

__LEADERBOARDS_URL_TEMPLATE = app.config['APP_URL'] + 'leaderboards/{comp_id}/'

__URL_ROOT = environ.get('APP_URL', 'http://fake.url.com/')
__PROFILE_URL = __URL_ROOT + 'u/{username}'

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
    for comp_event in sort_comp_events_by_global_sort_order(list(comp.events)):
        results = list(get_all_complete_user_results_for_comp_event(comp_event.id))
        if not results:
            continue

        results_with_ranks = sort_user_results_with_rankings(results, comp_event.Event.eventFormat)

        post_body += __RESULTS_EVENT_HEADER_TEMPLATE.format(event_name=comp_event.Event.name)

        total_participants = len(results)
        for i, _, result in results_with_ranks:
            username = result.User.username
            if username not in user_points.keys():
                user_points[username] = 0
            user_points[username] += (total_participants - i)

            if i <= __USER_PER_EVENT_LIMIT:
                post_body += __RESULTS_USER_LINE_TEMPLATE.format(username=__escape_username(username),
                    profile_url=__profile_for(username), result=result.friendly_result())

    user_points = [(username, points) for username, points in user_points.items()]
    user_points.sort(key=lambda x: x[1], reverse=True)

    post_body += __RESULTS_POINTS_SECTION_HEADER
    for username, points in user_points[:__USER_LIMIT_IN_POINTS]:
        post_body += __RESULTS_USER_POINTS_TEMPLATE.format(username=__escape_username(username),
            profile_url=__profile_for(username), points=points)

    if not is_rerun:
        new_post_id = submit_post(title, post_body)
        comp.result_thread_id = new_post_id
        save_competition(comp)
    else:
        results_thread_id = comp.result_thread_id
        update_post(post_body, results_thread_id)

# -------------------------------------------------------------------------------------------------

def __escape_username(username):
    """ Escapes a username so certain character combinations don't show up with Markdown formatting
    in the Reddit post. """

    username = username.replace('_', r'\_')
    return username


def __profile_for(username):
    """ Returns the URL to the specified user's cubers.io profile. The "right" way to do this would
    generally be to do a `url_for(...)` but that only works when an app context is loaded, and this
    scoring script is run outside of the app context. """

    return __PROFILE_URL.format(username=username)
