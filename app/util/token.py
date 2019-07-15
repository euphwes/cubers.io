import random, string

from flask import session

def generate_token():
    """ Generates a token which will be be used for protection against Anti-Forgery """
    token_chars = string.ascii_letters + string.digits + '!@#$%^&*()_+-=~[]'
    token = ''.join(random.choices(token_chars, k=128))

    session['csrf-token'] = token

def valid_token(input_token):
    """ Compares the token in the session """
    return session['csrf-token'] == input_token
