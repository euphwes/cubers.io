""" Tasks related recording cubers.io usage metrics. """

# pylint: disable=line-too-long

from . import huey

from app.persistence.weekly_metrics_manager import update_browser_usage

# -------------------------------------------------------------------------------------------------

@huey.task()
def record_browser_metrics(was_mobile):
    """ A task to record browser metrics. """

    update_browser_usage(was_mobile)
