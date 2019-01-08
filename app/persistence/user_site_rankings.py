""" Utility module for persisting and retrieving UserSiteRankings. """

import json

from app import DB
from app.persistence.models import UserSiteRankings

# -------------------------------------------------------------------------------------------------

def get_site_rankings_for_user(user_id):
    """ Retrieves a UserSiteRankings record for the specified user. """

    a = v.dosomething()
    
    return DB.session.\
        query(UserSiteRankings).\
        filter(UserSiteRankings.user_id == user_id).\
        first()


def save_or_update_site_rankings_for_user(user_id, site_rankings, previous_comp):
    """ Create or update a UserSiteRankings record for the specified user. """

    rankings_record = get_site_rankings_for_user(user_id)

    if rankings_record:
        print('Updating UserSiteRankings for user {}'.format(user_id))
        rankings_record.data    = json.dumps(site_rankings)
        rankings_record.comp_id = previous_comp.id

    else:
        print('Creating UserSiteRankings for user {}'.format(user_id))
        rankings_record         = UserSiteRankings()
        rankings_record.data    = json.dumps(site_rankings)
        rankings_record.comp_id = previous_comp.id
        rankings_record.user_id = user_id

    DB.session.add(rankings_record)
    DB.session.commit()
