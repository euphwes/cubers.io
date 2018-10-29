#pylint: disable=C0111
from .auth import login, logout, authorize
from .home import index
from .admin import gc_select, gc_select_user
from .util import current_comp, prev_results, current_title
from .results import results_list