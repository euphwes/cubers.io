""" Root of routes package. """

from functools import wraps

from flask import abort


def api_login_required(func):

    # TODO can we use this or similar in profile routes for the admin stuff?
    # TODO can we use this or similar in leaderboards routes for admin stuff?

    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return abort(HTTPStatus.UNAUTHORIZED)

        return func(*args, **kwargs)

    return decorated_function


from cubersio.routes.admin.gift_codes import *
from cubersio.routes.auth import *
from cubersio.routes.auth.reddit import *
from cubersio.routes.auth.wca import *
from cubersio.routes.events.event_routes import *
from cubersio.routes.events.kinchranks_routes import *
from cubersio.routes.events.sum_of_ranks_routes import *
from cubersio.routes.export.export_routes import *
from cubersio.routes.home.home_routes import *
from cubersio.routes.persistence.persistence_routes import *
from cubersio.routes.results.results_routes import *
from cubersio.routes.timer.timer_routes import *
from cubersio.routes.user.profile_routes import *
from cubersio.routes.user.versus_routes import *
from cubersio.routes.user.settings import *
from cubersio.routes.user.settings.custom_colors_settings_routes import *
from cubersio.routes.user.settings.event_settings_routes import *
from cubersio.routes.user.settings.reddit_settings_routes import *
from cubersio.routes.user.settings.timer_settings_routes import *
from cubersio.routes.user.settings.wca_settings_routes import *
