""" Utility module for persisting and retrieving UserSiteRankings. """

import json

from app import DB
from app.persistence.models import UserSiteRankings

# -------------------------------------------------------------------------------------------------

def get_site_rankings_for_user(user_id):
    """ Retrieves a UserSiteRankings record for the specified user. """

    return DB.session.\
        query(UserSiteRankings).\
        filter(UserSiteRankings.user_id == user_id).\
        first()


def get_all_user_site_rankings():
    """ Retrieves all UserSiteRankings records. """

    return DB.session.\
        query(UserSiteRankings).\
        all()


def save_or_update_site_rankings_for_user(user_id, new_user_site_rankings):
    """ Create or update a UserSiteRankings record for the specified user. """

    rankings_record = get_site_rankings_for_user(user_id)

    # If this user already has a site rankings record, just update it
    if rankings_record:
        rankings_record.data = new_user_site_rankings.data
        rankings_record.timestamp = new_user_site_rankings.timestamp
        rankings_record.sum_all_single = new_user_site_rankings.sum_all_single
        rankings_record.sum_all_average = new_user_site_rankings.sum_all_average
        rankings_record.sum_wca_single = new_user_site_rankings.sum_wca_single
        rankings_record.sum_wca_average = new_user_site_rankings.sum_wca_average
        rankings_record.sum_non_wca_single = new_user_site_rankings.sum_non_wca_single
        rankings_record.sum_non_wca_average = new_user_site_rankings.sum_non_wca_average
        DB.session.add(rankings_record)

    # If not, create a new one
    else:
        new_user_site_rankings.user_id = user_id
        DB.session.add(new_user_site_rankings)

    DB.session.commit()


def update_one_event_site_rankings_for_user(user_id, new_site_rankings, event):
    """ Update just one event's info for a user's UserSiteRankings if the record already exists.
    dict[event ID][(single, single_site_ranking, average, average_site_ranking)] """

    rankings_record = get_site_rankings_for_user(user_id)

    # Rankings record doesn't yet exist for this user, no need to create a new one
    if not rankings_record:
        return

    #print('Updating UserSiteRankings for user {} and event {}'.format(user_id, event.id))

    # Get dict representation of existing site rankings data, and then update the entry
    # for the specified event with the new data for that event
    existing_data = rankings_record.get_site_rankings_data_as_dict()
    existing_data[event.id] = new_site_rankings[event.id]

    # Serialize the modified rankings data back into the rankings record
    rankings_record.data = json.dumps(existing_data)

    DB.session.add(rankings_record)
    DB.session.commit()
