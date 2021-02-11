""" Utility functions for interacting with WCA via OAuth """

from urllib.parse import urlencode

from requests import post as post_request, get as get_request

from cubersio import app


__REDIRECT      = app.config['WCA_REDIRECT_URI']
__CLIENT_ID     = app.config['WCA_CLIENT_ID']
__CLIENT_SECRET = app.config['WCA_CLIENT_SECRET']
__APP_URL       = app.config['APP_URL']
__IS_DEVO       = app.config['IS_DEVO']
__RESPONSE_TYPE = 'code'

__OAUTH_SCOPES = ['public']

__AUTH_URL_BASE    = 'https://www.worldcubeassociation.org/oauth/authorize?'
__WCA_ME_API_URL   = 'https://www.worldcubeassociation.org/api/v0/me'
__ACCESS_TOKEN_URL = 'https://www.worldcubeassociation.org/oauth/token'


class WCAAuthException(Exception):
    """ Generic exception indicating there was an error code return in a WCA OAuth response. """


def get_wca_auth_url(state: str = '...') -> str:
    """ Returns a url for authenticating with the WCA. """

    wca_auth_query_params = urlencode({
        'state': state,
        'scope': ' '.join(__OAUTH_SCOPES),
        'client_id': __CLIENT_ID,
        'redirect_uri': __REDIRECT,
        'response_type': __RESPONSE_TYPE
    })

    return __AUTH_URL_BASE + wca_auth_query_params


def get_wca_access_token_from_auth_code(auth_code: str) -> str:
    """ Calls to the WCA with the auth code, and cubers.io client ID and secret, to retrieve the access token for the
    authenticated user. """

    payload = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'client_id': __CLIENT_ID,
        'client_secret': __CLIENT_SECRET,
        'redirect_uri': __REDIRECT,
    }

    response = post_request(__ACCESS_TOKEN_URL, data=payload).json()

    error = response.get('error', None)
    if error:
        raise WCAAuthException(error)

    return response['access_token']


def get_wca_id_from_access_token(access_token: str) -> str:
    """ Returns the user's WCA ID from the /me WCA API endpoint. """

    headers = {"Authorization": "Bearer " + access_token}
    me_data = get_request(__WCA_ME_API_URL, headers=headers).json()

    return me_data['me']['wca_id']
