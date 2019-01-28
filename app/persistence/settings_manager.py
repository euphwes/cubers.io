""" Utility module for persisting and retrieving user settings. """

from app import DB
from app.persistence.models import UserSetting

# -------------------------------------------------------------------------------------------------

TRUE_STR  = 'true'
FALSE_STR = 'false'

# Constants which correspond to a `setting_code` in the UserSettings database table
# pylint: disable=R0903,C0111
class SettingCode():
    USE_INSPECTION_TIME    = 'use_inspection_time'
    HIDE_RUNNING_TIMER     = 'hide_running_timer'
    REDDIT_COMP_NOTIFY     = 'reddit_comp_notify'
    DEFAULT_TO_MANUAL_TIME = 'manual_time_entry_by_default'

# Default values for each `setting_code`
SETTING_DEFAULTS = {
    SettingCode.USE_INSPECTION_TIME    : FALSE_STR,
    SettingCode.HIDE_RUNNING_TIMER     : FALSE_STR,
    SettingCode.REDDIT_COMP_NOTIFY     : FALSE_STR,
    SettingCode.DEFAULT_TO_MANUAL_TIME : FALSE_STR
}

# Acceptable values for each `setting_code`.
# If a setting code doesn't have an entry here, the value is unconstrained.
SETTING_ALLOWED_VALUES = {
    SettingCode.USE_INSPECTION_TIME    : [FALSE_STR, TRUE_STR],
    SettingCode.HIDE_RUNNING_TIMER     : [FALSE_STR, TRUE_STR],
    SettingCode.REDDIT_COMP_NOTIFY     : [FALSE_STR, TRUE_STR],
    SettingCode.DEFAULT_TO_MANUAL_TIME : [FALSE_STR, TRUE_STR]
}

# -------------------------------------------------------------------------------------------------

def __create_unset_setting(user_id, setting_code):
    """ Creates a UserSetting for the specified user and setting code, with a default value. """

    if setting_code not in SETTING_DEFAULTS:
        raise ValueError("That setting doesn't exist!")

    setting_value = SETTING_DEFAULTS[setting_code]
    user_setting  = UserSetting(user_id=user_id, setting_code=setting_code,\
        setting_value=setting_value)

    DB.session.add(user_setting)
    DB.session.commit()

    return user_setting


def get_default_value_for_setting(setting_code):
    """ Retrieves a default value for a particular setting code. """

    if setting_code not in SETTING_DEFAULTS:
        raise ValueError("That setting doesn't exist!")

    return SETTING_DEFAULTS[setting_code]


def get_setting_for_user(user_id, setting_code):
    """ Retrieves a user's setting for a given setting code. """

    setting = DB.session.\
        query(UserSetting).\
        filter(UserSetting.user_id == user_id).\
        filter(UserSetting.setting_code == setting_code).\
        first()

    return setting.setting_value if setting \
        else __create_unset_setting(user_id, setting_code).setting_value


def set_setting_for_user(user_id, setting_code, setting_value):
    """ Sets a user's setting for a given setting code. """

    allowed_values = SETTING_ALLOWED_VALUES.get(setting_code, None)
    if allowed_values and setting_value not in allowed_values:
        raise ValueError("{} is not an allowed value for {}".format(setting_value, setting_code))

    setting = DB.session.\
        query(UserSetting).\
        filter(UserSetting.user_id == user_id).\
        filter(UserSetting.setting_code == setting_code).\
        first()

    if not setting:
        setting = __create_unset_setting(user_id, setting_code)

    setting.setting_value = setting_value
    DB.session.add(setting)
    DB.session.commit()

    return setting
