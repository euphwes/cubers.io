""" Utility module for providing access to business logic for users. """

from app import DB
from app.persistence.models import User
# -------------------------------------------------------------------------------------------------

def get_all_users():
    """ Get all users. """
    return User.query.all()


def update_or_create_user(username, refresh_token):
    """ Updates a user with the provided refresh token, or creates a new user. Returns the user. """
    user = get_user_by_username(username)

    if user:
        user.refresh_token = refresh_token
    else:
        user = User(username=username, refresh_token=refresh_token)
        DB.session.add(user)

    DB.session.commit()
    return user


def get_user_by_username(username):
    """ Returns the user with this username, or else `None` if no such user exists. """
    return User.query.filter_by(username=username).first()
