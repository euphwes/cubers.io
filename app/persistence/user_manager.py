""" Utility module for persisting and retrieving users. """

from typing import Optional

from app import DB
from app.persistence.models import User, UserEventResults
from app.persistence.weekly_metrics_manager import increment_new_user_count

# -------------------------------------------------------------------------------------------------

class UserDoesNotExistException(Exception):
    """ An error raised when an attempting an operation on a user which does not exist. """

    def __init__(self, username):
        self.username = username
        super(UserDoesNotExistException, self).__init__()

    def __str__(self):
        return "There is no user with the username '{}'".format(self.username)

# -------------------------------------------------------------------------------------------------

def get_all_users():
    """ Get all users. """

    return User.query.all()


def get_all_active_usernames():
    """ Get all usernames for users with at least one UserEventResults. """

    # list of 1-tuples of usernames
    usernames = User.query.with_entities(User.username).\
        join(UserEventResults).\
        distinct(User.id).\
        all()

    return sorted([r[0] for r in usernames])


def get_user_count():
    """ Returns the total number of users. """

    return User.query.count()


def update_or_create_user(username, refresh_token):
    """ Creates or updates a user with the provided refresh token. Returns the user. """

    user = get_user_by_username(username)

    if user:
        user.refresh_token = refresh_token
    else:
        user = User(username=username, refresh_token=refresh_token)
        DB.session.add(user)
        increment_new_user_count()

    DB.session.commit()
    return user


def get_user_by_username(username) -> Optional[User]:
    """ Returns the user with this username, or else `None` if no such user exists. """

    return User.query.filter_by(username=username).first()


def get_user_by_id(user_id) -> Optional[User]:
    """ Returns the user with this user_id, or else `None` if no such user exists. """

    return User.query.filter_by(id=user_id).first()


def set_user_as_admin(username):
    """ Sets admin status for a user. Raises UserDoesNotExistException if no such user exists. """

    user = get_user_by_username(username)
    if not user:
        raise UserDoesNotExistException(username)

    user.is_admin = True
    DB.session.add(user)
    DB.session.commit()


def unset_user_as_admin(username):
    """ Removes admin status for a user. Raises UserDoesNotExistException if user doesn't exist. """

    user = get_user_by_username(username)
    if not user:
        raise UserDoesNotExistException(username)

    user.is_admin = False
    DB.session.add(user)
    DB.session.commit()


def set_perma_blacklist_for_user(user_id):
    """ Sets permanent blacklist flag for a user. """

    user = get_user_by_id(user_id)
    if not user:
        return

    user.always_blacklist = True
    DB.session.add(user)
    DB.session.commit()


def unset_perma_blacklist_for_user(user_id):
    """ Removes permanent blacklist flag for a user. """

    user = get_user_by_id(user_id)
    if not user:
        return

    user.always_blacklist = False
    DB.session.add(user)
    DB.session.commit()


def verify_user(user_id):
    """ Sets verified flag for a user. """

    user = get_user_by_id(user_id)
    if not user:
        return

    user.is_verified = True
    DB.session.add(user)
    DB.session.commit()


def unverify_user(user_id):
    """ Removes verified flag for a user. """

    user = get_user_by_id(user_id)
    if not user:
        return

    user.is_verified = False
    DB.session.add(user)
    DB.session.commit()


def set_user_as_results_moderator(username):
    """ Sets results moderator status for a user. Raises UserDoesNotExistException if no such user exists. """

    user = get_user_by_username(username)
    if not user:
        raise UserDoesNotExistException(username)

    user.is_results_mod = True
    DB.session.add(user)
    DB.session.commit()


def unset_user_as_results_moderator(username):
    """ Removes results moderator status for a user. Raises UserDoesNotExistException if user doesn't exist. """

    user = get_user_by_username(username)
    if not user:
        raise UserDoesNotExistException(username)

    user.is_results_mod = False
    DB.session.add(user)
    DB.session.commit()


def get_all_admins():
    """ Returns a list of all admin users. """

    return User.query.\
        filter_by(is_admin=True).\
        all()


def get_username_id_map():
    """ Returns a map of all user's username to their ID. """

    mapping = dict()
    for user in get_all_users():
        mapping[user.username] = user.id

    return mapping
