""" Utility module for providing access to business logic for users. """

from app import DB
from app.persistence.models import User, Blacklist

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


def blacklist_user_for_competition(username, comp_id):
    """ Adds an entry to the database blacklisting the user for the specified competition. """

    user = get_user_by_username(username)
    if not user:
        raise ValueError("Oops, that user doesn't exist.")

    blacklist_entry = Blacklist()
    blacklist_entry.user_id = user.id
    blacklist_entry.comp_id = comp_id

    DB.session.add(blacklist_entry)
    DB.session.commit()


def get_blacklisted_users_for_competition(comp_id):
    """ Returns a list of users blacklisted for the specified competition. """

    return [entry.user for entry in Blacklist.query.filter_by(comp_id=comp_id).all()]


def get_comp_userlist_blacklist_map():
    """ Returns a mapping of blacklisted users to the comps they were blacklisted from:
    dict[competition_id][list(user_id)] """

    mapping = dict()
    for entry in Blacklist.query.all():
        user_id = entry.user_id
        comp_id = entry.comp_id
        if comp_id not in mapping.keys():
            mapping[comp_id] = list()
        mapping[comp_id].append(user_id)

    return mapping
        