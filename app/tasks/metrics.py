""" Tasks related recording cubers.io usage metrics. """

from app.persistence.weekly_metrics_manager import update_browser_usage, increment_new_user_count

from . import huey

# -------------------------------------------------------------------------------------------------

@huey.task()
def record_browser_metrics(was_mobile):
    """ A task to record browser metrics. """

    update_browser_usage(was_mobile)


@huey.task()
def record_new_user():
    """ A task to record new user metrics. """

    increment_new_user_count()