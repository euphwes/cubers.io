""" Utility module for persisting and retrieving weekly blacklist records. """

from typing import Optional

from app import DB, app
from app.persistence.models import WeeklyBlacklist, User

# -------------------------------------------------------------------------------------------------

__LOG_CREATED_WEEKLY_BLACKLIST = 'Created WeeklyBlacklist record for {username}'
__LOG_CLEARED_WEEKLY_BLACKLIST = 'Cleared all WeeklyBlacklist entries.'

# -------------------------------------------------------------------------------------------------
# Functions and types below are intended to be used directly.
# -------------------------------------------------------------------------------------------------

def ensure_weekly_blacklist_for_user(user: User) -> None:
    """ Creates a weekly blacklist record for the specified user if it doesn't already exist.
    If it does exist, take no action. """

    if get_weekly_blacklist_entry_by_user_id(user.id):
        return

    weekly_blacklist_record = WeeklyBlacklist(user_id=user.id)
    DB.session.add(weekly_blacklist_record)
    DB.session.commit()

    app.logger.info(__LOG_CREATED_WEEKLY_BLACKLIST.format(username=user.username),
        extra={'user_id': user.id, 'username': user.username})


def get_weekly_blacklist_entry_by_user_id(user_id: int) -> Optional[WeeklyBlacklist]:
    """ Returns the weekly blacklist record with this user_id, or else `None` if no such record exists. """

    return WeeklyBlacklist.query.filter_by(user_id=user_id).first()


def clearly_weekly_blacklist() -> None:
    """ Deletes all records in this table. Used when a new competition is posted so all users can start
    the week with a clean slate. """

    for record in WeeklyBlacklist.query.all():
        DB.session.delete(record)

    DB.session.commit()

    app.logger.info(__LOG_CLEARED_WEEKLY_BLACKLIST)
