""" Utility module for adding, retrieving, and updating SCS gift codes in the code pool. """

from typing import List

from app import DB
from app.persistence.models import SCSGiftCodePool

#--------------------------------------------------------------------------------------------------

def bulk_add_gift_codes(gift_codes: List[str]) -> None:
    """ Add SCS gift codes to the database. """

    for gift_code in gift_codes:
        DB.session.add(SCSGiftCodePool(gift_code=gift_code, used=False))

    DB.session.commit()


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


def mark_gift_code_used(gift_code_id : int) -> None:
    """ Marks the gift code with the supplied ID as used and saves the record. """

    gift_code = SCSGiftCodePool.query.get(gift_code_id)
    gift_code.used = True

    DB.session.add(gift_code)
    DB.session.commit()
