""" Core task setup. """

from queue_config import huey

from .admin_notification import *
from .competition_management import *
from .reddit import *
from .scramble_generation import *
