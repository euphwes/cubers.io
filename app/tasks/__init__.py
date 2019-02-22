""" Core task setup. """

from queue_config import huey

from .admin_notification import notify_admin
from .competition_management import wrap_weekly_competition
from .scramble_generation import check_scramble_pool, top_off_scramble_pool
from .metrics import record_browser_metrics
