""" Utility module for recording and managing weekly competition metrics. """

from app import DB
from app.persistence.models import WeeklyMetrics
from app.persistence.comp_manager import get_active_competition

# -------------------------------------------------------------------------------------------------

def create_new_weekly_metrics_for_comp(comp_id):
    """ Creates and returns a new weekly metrics record for the specified competition. """

    metrics = WeeklyMetrics(comp_id=comp_id)
    DB.session.add(metrics)
    DB.session.commit()

    return metrics


def get_weekly_metrics(comp_id):
    """ Retrieves the weekly metrics record for the specified competition. """

    metrics = DB.session.\
        query(WeeklyMetrics).\
        filter(WeeklyMetrics.comp_id == comp_id).\
        first()

    return metrics if metrics else create_new_weekly_metrics_for_comp(comp_id)


def save_metrics(metrics):
    """ Saves a metrics record. """

    DB.session.add(metrics)
    DB.session.commit()


def update_browser_usage(was_mobile, comp_id=None):
    """ Increments mobile hit count if `was_mobile` otherwise increments desktop hit count.
    If comp_id is specified, uses that competition's metrics, otherwise uses the metrics for the
    current week's competition. """

    if not comp_id:
        comp_id = get_active_competition().id

    metrics = get_weekly_metrics(comp_id)

    if was_mobile:
        if not metrics.mobile_hits:
            metrics.mobile_hits = 1
        else:
            metrics.mobile_hits += 1
    else:
        if not metrics.desktop_hits:
            metrics.desktop_hits = 1
        else:
            metrics.desktop_hits += 1

    save_metrics(metrics)


def increment_new_user_count(comp_id=None):
    """ Increments new user count. If comp_id is specified, uses that competition's metrics,
    otherwise uses the metrics for the current week's competition.  """

    if not comp_id:
        comp_id = get_active_competition().id

    metrics = get_weekly_metrics(comp_id)

    if not metrics.new_users_count:
        metrics.new_users_count = 1
    else:
        metrics.new_users_count += 1

    save_metrics(metrics)
