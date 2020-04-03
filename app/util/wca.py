""" Utility functions for dealing with WCA OAuth. """

from app import app

# -------------------------------------------------------------------------------------------------

__REDIRECT         = app.config['WCA_REDIRECT_URI']
__CLIENT_ID        = app.config['WCA_CLIENT_ID']
__CLIENT_SECRET    = app.config['WCA_CLIENT_SECRET']
__APP_URL          = app.config['APP_URL']
__IS_DEVO          = app.config['IS_DEVO']

__OAUTH_SCOPES = ['public']

# -------------------------------------------------------------------------------------------------
