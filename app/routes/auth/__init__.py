""" Routes related to authentication, common to both WCA and Reddit. Also includes common utility
functions and variables. """

from base64 import urlsafe_b64decode, urlsafe_b64encode

from flask import request, redirect, url_for, render_template
from flask_login import current_user, logout_user

from app import app
from app.util.simplecrypt import encrypt, decrypt

# -------------------------------------------------------------------------------------------------
# Common auth routes
# -------------------------------------------------------------------------------------------------

@app.route("/logout")
def logout():
    """ Log out the current user. """

    if current_user.is_authenticated:
        logout_user()

    return redirect(url_for('index'))


@app.route('/denied')
def denied():
    """ When the user declines OAuth, acknowledge and show that. """

    return render_template(__LOGIN_DENIED_TEMPLATE_PATH)

# -------------------------------------------------------------------------------------------------

__SECRET_KEY = app.config['FLASK_SECRET_KEY']
__LOGIN_DENIED_TEMPLATE_PATH = 'prompt_login/denied.html'

# -------------------------------------------------------------------------------------------------

def __encrypt_state(state):
    """ Encrypts a given string using simple-crypt (resulting in a byte array), then base64 encodes
    the byte array to make it a URL-safe string. """

    return urlsafe_b64encode(encrypt(__SECRET_KEY, state))


def __decrypt_state(state):
    """ Base64 decodes a given string into a byte array, which is decrypted using simple-crypt and
    then decoded back to the original string. """

    return decrypt(__SECRET_KEY, urlsafe_b64decode(state)).decode('utf-8')
