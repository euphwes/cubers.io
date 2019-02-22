""" Tasks related recording cubers.io usage metrics. """

from user_agents import parse as parse_user_agent

from app.persistence.weekly_metrics_manager import update_browser_usage, increment_new_user_count,\
    update_bot_hits

from . import huey

# -------------------------------------------------------------------------------------------------

@huey.task()
def record_browser_metrics(was_mobile, user_agent):
    """ A task to record browser metrics. """

    if parse_user_agent(user_agent.string).is_bot:
        update_bot_hits()
    else:
        update_browser_usage(was_mobile)


@huey.task()
def record_new_user():
    """ A task to record new user metrics. """

    increment_new_user_count()
