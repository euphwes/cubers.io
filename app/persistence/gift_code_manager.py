""" Utility module for adding, retrieving, and updating SCS gift codes in the code pool. """

from uuid import uuid1
from typing import List

from app import DB
from app.persistence.models import SCSGiftCodePool, WeeklyCodeRecipientConfirmDeny, WeeklyCodeRecipientResolution

#--------------------------------------------------------------------------------------------------

__NEW_UUID = lambda: str(uuid1())

#--------------------------------------------------------------------------------------------------

def bulk_add_gift_codes(gift_codes: List[str]) -> None:
    """ Add SCS gift codes to the database. """

    for gift_code in gift_codes:
        DB.session.add(SCSGiftCodePool(gift_code=gift_code, used=False))

    DB.session.commit()


def get_gift_code_by_id(gift_code_id: int) -> SCSGiftCodePool:
    """ Retrieves a gift code by ID. """

    return DB.session.\
        query(SCSGiftCodePool).\
        filter(SCSGiftCodePool.id == gift_code_id).\
        first()


def get_unused_gift_code() -> SCSGiftCodePool:
    """ Retrieves an unused gift code. """

    return DB.session.\
        query(SCSGiftCodePool).\
        filter(SCSGiftCodePool.used.is_(False)).\
        first()


def get_unused_gift_code_count() -> int:
    """ Returns the number of unused gift codes remaining in the database. """

    return DB.session.\
        query(SCSGiftCodePool).\
        filter(SCSGiftCodePool.used.is_(False)).\
        count()


def mark_gift_code_used(gift_code_id: int) -> None:
    """ Marks the gift code with the supplied ID as used and saves the record. """

    gift_code = SCSGiftCodePool.query.get(gift_code_id)
    gift_code.used = True

    DB.session.add(gift_code)
    DB.session.commit()


def create_confirm_deny_record(gift_code_id: int, user_id: int, comp_id: int) -> WeeklyCodeRecipientConfirmDeny:
    """ Creates and returns a WeeklyCodeRecipientConfirmDeny record for the specified gift code,
    user, and competition. """

    confirm_deny_record = WeeklyCodeRecipientConfirmDeny(gift_code_id=gift_code_id, user_id=user_id,
        comp_id=comp_id, confirm_code=__NEW_UUID(), deny_code=__NEW_UUID())

    DB.session.add(confirm_deny_record)
    DB.session.commit()

    return confirm_deny_record


def update_confirm_deny_record(confirm_deny_record: WeeklyCodeRecipientConfirmDeny) -> None:
    """ Updates a WeeklyCodeRecipientConfirmDeny record and saves it to the database. """

    DB.session.add(confirm_deny_record)
    DB.session.commit()


def get_pending_confirm_deny_record_by_deny_code(deny_code: str) -> WeeklyCodeRecipientConfirmDeny:
    """ Returns the WeeklyCodeRecipientConfirmDeny with the deny_code that matches. """

    return DB.session.\
        query(WeeklyCodeRecipientConfirmDeny).\
        filter(WeeklyCodeRecipientConfirmDeny.deny_code == deny_code).\
        filter(WeeklyCodeRecipientConfirmDeny.resolution == WeeklyCodeRecipientResolution.Pending).\
        first()


def get_pending_confirm_deny_record_by_confirm_code(confirm_code: str) -> WeeklyCodeRecipientConfirmDeny:
    """ Returns the WeeklyCodeRecipientConfirmDeny with the confirm_code that matches. """

    return DB.session.\
        query(WeeklyCodeRecipientConfirmDeny).\
        filter(WeeklyCodeRecipientConfirmDeny.confirm_code == confirm_code).\
        filter(WeeklyCodeRecipientConfirmDeny.resolution == WeeklyCodeRecipientResolution.Pending).\
        first()
