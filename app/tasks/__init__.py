""" Core task setup. """

from queue_config import huey

from .admin_notification import notify_admin
from .competition_generation import wrap_weekly_competition, check_scramble_pool
