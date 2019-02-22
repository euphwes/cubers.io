""" Tasks related recording cubers.io usage metrics. """

# pylint: disable=line-too-long

from . import huey

# -------------------------------------------------------------------------------------------------

@huey.task()
def record_browser_metrics(was_mobile):
    """ A task to record browser metrics. """

    pass