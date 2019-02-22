""" Root of routes package. """

from functools import wraps

from flask import request

from app.tasks.metrics import record_browser_metrics

def record_usage_metrics(route_func):
    """ A route decorator which records various metrics related to usage.  """

    @wraps(route_func)
    def wrapped_route(*args, **kwargs):
        record_browser_metrics(request.MOBILE)
        return route_func(*args, **kwargs)

    return wrapped_route

# -------------------------------------------------------------------------------------------------

from .auth import login, logout, authorize
from .home import index
from .admin import gc_select, gc_select_user
from .util import current_comp, prev_results, is_admin_viewing
from .results import results_list
from .user import profile, edit_settings
from .events import event_results, sum_of_ranks, event_results_export
