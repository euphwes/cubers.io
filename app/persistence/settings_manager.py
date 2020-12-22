""" Utility module for persisting and retrieving user settings. """

from collections import namedtuple
from itertools import zip_longest

from app import DB
from app.persistence.models import UserSetting

# -------------------------------------------------------------------------------------------------

# Constants which correspond to a `setting_code` in the UserSettings database table
# pylint: disable=R0903,C0111
class SettingCode():
    # Timer settings
    USE_INSPECTION_TIME          = 'use_inspection_time'
    HIDE_INSPECTION_TIME         = 'hide_inspection_time'
    USE_INSPECTION_AUDIO_WARNING = 'use_inspection_audio_warning'
    HIDE_RUNNING_TIMER           = 'hide_running_timer'
    DEFAULT_TO_MANUAL_TIME       = 'manual_time_entry_by_default'
    HIDE_SCRAMBLE_PREVIEW        = 'hide_scramble_preview'
    ENABLE_MOVING_SHAPES_BG      = 'enable_moving_shapes_bg'

    # Hidden events
    HIDDEN_EVENTS = 'hidden_events'

    # WCA id settings
    SHOW_WCA_ID = 'show_wca_id'

    # Reddit related settings
    REDDIT_COMP_NOTIFY    = 'reddit_comp_notify'
    REDDIT_RESULTS_NOTIFY = 'reddit_results_notify'

    # Custom cube colors
    USE_CUSTOM_CUBE_COLORS = 'use_custom_cube_colors'
    CUSTOM_CUBE_COLOR_U    = 'custom_cube_color_U'
    CUSTOM_CUBE_COLOR_F    = 'custom_cube_color_F'
    CUSTOM_CUBE_COLOR_R    = 'custom_cube_color_R'
    CUSTOM_CUBE_COLOR_D    = 'custom_cube_color_D'
    CUSTOM_CUBE_COLOR_B    = 'custom_cube_color_B'
    CUSTOM_CUBE_COLOR_L    = 'custom_cube_color_L'

    # Custom pyraminx colors
    USE_CUSTOM_PYRAMINX_COLORS = 'use_custom_pyraminx_colors'
    CUSTOM_PYRAMINX_COLOR_F    = 'custom_pyra_color_F'
    CUSTOM_PYRAMINX_COLOR_L    = 'custom_pyra_color_L'
    CUSTOM_PYRAMINX_COLOR_R    = 'custom_pyra_color_R'
    CUSTOM_PYRAMINX_COLOR_D    = 'custom_pyra_color_D'

    # Custom megaminx colors
    USE_CUSTOM_MEGAMINX_COLORS = 'use_custom_megaminx_colors'
    CUSTOM_MEGAMINX_COLOR_1    = 'custom_mega_color_1'
    CUSTOM_MEGAMINX_COLOR_2    = 'custom_mega_color_2'
    CUSTOM_MEGAMINX_COLOR_3    = 'custom_mega_color_3'
    CUSTOM_MEGAMINX_COLOR_4    = 'custom_mega_color_4'
    CUSTOM_MEGAMINX_COLOR_5    = 'custom_mega_color_5'
    CUSTOM_MEGAMINX_COLOR_6    = 'custom_mega_color_6'
    CUSTOM_MEGAMINX_COLOR_7    = 'custom_mega_color_7'
    CUSTOM_MEGAMINX_COLOR_8    = 'custom_mega_color_8'
    CUSTOM_MEGAMINX_COLOR_9    = 'custom_mega_color_9'
    CUSTOM_MEGAMINX_COLOR_10   = 'custom_mega_color_10'
    CUSTOM_MEGAMINX_COLOR_11   = 'custom_mega_color_11'
    CUSTOM_MEGAMINX_COLOR_12   = 'custom_mega_color_12'

    # Custom FTO colors
    USE_CUSTOM_FTO_COLORS = 'use_custom_fto_colors'
    CUSTOM_FTO_COLOR_U    = 'custom_fto_color_U'
    CUSTOM_FTO_COLOR_F    = 'custom_fto_color_F'
    CUSTOM_FTO_COLOR_R    = 'custom_fto_color_R'
    CUSTOM_FTO_COLOR_D    = 'custom_fto_color_D'
    CUSTOM_FTO_COLOR_B    = 'custom_fto_color_B'
    CUSTOM_FTO_COLOR_L    = 'custom_fto_color_L'
    CUSTOM_FTO_COLOR_BR   = 'custom_fto_color_BR'
    CUSTOM_FTO_COLOR_BL   = 'custom_fto_color_BL'

    # Custom Square-1 colors
    USE_CUSTOM_SQUAN_COLORS = 'use_custom_squan_colors'
    CUSTOM_SQUAN_COLOR_U    = 'custom_squan_color_U'
    CUSTOM_SQUAN_COLOR_F    = 'custom_squan_color_F'
    CUSTOM_SQUAN_COLOR_R    = 'custom_squan_color_R'
    CUSTOM_SQUAN_COLOR_D    = 'custom_squan_color_D'
    CUSTOM_SQUAN_COLOR_B    = 'custom_squan_color_B'
    CUSTOM_SQUAN_COLOR_L    = 'custom_squan_color_L'


# Denotes the type of setting, aka boolean, free-form text, etc
class SettingType():
    BOOLEAN        = 'boolean'
    HEX_COLOR      = 'hex_color'      # hex color code aka "#FFC1D2"
    EVENT_ID_LIST  = 'event_id_list'  # comma-delimited list of integers


# Encapsulates necessary information about each setting
class SettingInfo():
    def __init__(self, title, validator, setting_type, default_value, affects=None, opposite_affects=False):
        self.title = title
        self.validator = validator
        self.setting_type = setting_type
        self.default_value = default_value
        self.affects = affects  # an optional list of SettingCodes this code disables if disabled
        self.opposite_affects = opposite_affects  # if this is True, the affects list is disabled if this setting is on

# -------------------------------------------------------------------------------------------------

TRUE_STR  = 'true'
FALSE_STR = 'false'

DEFAULT_CUBE_COLORS = {
    'U': '#FFFFFF',
    'F': '#00FF00',
    'R': '#FF0000',
    'D': '#FFFF00',
    'B': '#0000FF',
    'L': '#FF8800',
}

DEFAULT_PYRA_COLORS = {
    'F': '#00FF00',
    'L': '#FF0000',
    'R': '#0000FF',
    'D': '#FFFF00',
}

DEFAULT_MEGA_COLORS = {
    '1': '#FFFFFF',
    '2': '#DD0000',
    '3': '#006600',
    '4': '#8811FF',
    '5': '#FFCC00',
    '6': '#0000BB',
    '7': '#FFFFBB',
    '8': '#88DDFF',
    '9': '#FF8833',
    '10': '#77EE00',
    '11': '#FF99FF',
    '12': '#999999',
}

DEFAULT_FTO_COLORS = {
    'U': '#FFFFFF',
    'R': '#00FF00',
    'F': '#FF0000',
    'D': '#FFFF00',
    'B': '#0000FF',
    'L':  '#800080',
    'BL': '#FF8800',
    'BR': '#BEBEBE',
}

DEFAULT_SQUAN_COLORS = {
    'U': '#333333',
    'D': '#FFFFFF',
    'L': '#FF8800',
    'F': '#0000FF',
    'R': '#FF0000',
    'B': '#00FF00',
}

def boolean_validator(value):
    """ Validates a boolean setting value as text. """
    if value is None:
        return FALSE_STR
    if value in [True, False]:
        return str(value).lower()
    if value in [TRUE_STR, FALSE_STR]:
        return value
    raise ValueError("{} is not an acceptable value.".format(value))


HEX_CHARACTERS = set([c for c in 'ABCDEFabcdef0123456789'])

def hex_color_validator(value):
    """ Validates a string which represents a color in hex format. """

    if value[0] != "#":
        raise ValueError("{} is not a hex color value. It does not start with '#'.".format(value))

    for char in value[1:]:
        if char not in HEX_CHARACTERS:
            msg = "{} is not a hex color value. {} is not hexadecimal.".format(value, char)
            raise ValueError(msg)

    return value


def int_list_validator(value):
    """ Validates a string which should be a comma-delimited list of integers """

    # Empty string or None is ok, that means an empty list
    if not value:
        return ""

    for char in value.split(','):
        try:
            int(char)
        except ValueError:
            msg = '{} is not an integer, and so {} is not a valid integer list'.format(char, value)
            raise ValueError(msg)

    return value

# -------------------------------------------------------------------------------------------------

SETTING_INFO_MAP = {
    SettingCode.HIDDEN_EVENTS: SettingInfo(
        title         = "Hide Selected Events",
        validator     = int_list_validator,
        setting_type  = SettingType.EVENT_ID_LIST,
        default_value = ""
    ),

    SettingCode.SHOW_WCA_ID: SettingInfo(
        title         = "Show WCA ID on public profile",
        validator     = boolean_validator,
        setting_type  = SettingType.BOOLEAN,
        default_value = FALSE_STR
    ),

    SettingCode.HIDE_SCRAMBLE_PREVIEW: SettingInfo(
        title         = "Hide Scramble Preview",
        validator     = boolean_validator,
        setting_type  = SettingType.BOOLEAN,
        default_value = FALSE_STR
    ),

    SettingCode.DEFAULT_TO_MANUAL_TIME: SettingInfo(
        title            = "Use Manual Time Entry",
        validator        = boolean_validator,
        setting_type     = SettingType.BOOLEAN,
        default_value    = FALSE_STR,
        affects          = [SettingCode.USE_INSPECTION_TIME, SettingCode.HIDE_INSPECTION_TIME,
                            SettingCode.HIDE_RUNNING_TIMER],
        opposite_affects = True
    ),

    SettingCode.USE_INSPECTION_TIME: SettingInfo(
        title         = "Use\u00A0WCA\u00A015s\u00A0Inspection\u00A0Time (except\u00A0blind\u00A0events)",
        validator     = boolean_validator,
        setting_type  = SettingType.BOOLEAN,
        default_value = FALSE_STR,
        affects       = [SettingCode.HIDE_INSPECTION_TIME, SettingCode.USE_INSPECTION_AUDIO_WARNING]
    ),

    SettingCode.HIDE_INSPECTION_TIME: SettingInfo(
        title         = "Hide Inspection Time Countdown",
        validator     = boolean_validator,
        setting_type  = SettingType.BOOLEAN,
        default_value = FALSE_STR
    ),

    SettingCode.USE_INSPECTION_AUDIO_WARNING: SettingInfo(
        title         = "Use Inspection Time Audio Warning",
        validator     = boolean_validator,
        setting_type  = SettingType.BOOLEAN,
        default_value = FALSE_STR
    ),

    SettingCode.HIDE_RUNNING_TIMER: SettingInfo(
        title         = "Hide Timer While Running",
        validator     = boolean_validator,
        setting_type  = SettingType.BOOLEAN,
        default_value = FALSE_STR
    ),

    SettingCode.ENABLE_MOVING_SHAPES_BG: SettingInfo(
        title         = "Enable Animated Background",
        validator     = boolean_validator,
        setting_type  = SettingType.BOOLEAN,
        default_value = TRUE_STR
    ),

    SettingCode.REDDIT_RESULTS_NOTIFY: SettingInfo(
        title         = "Receive PM summarizing competition results",
        validator     = boolean_validator,
        setting_type  = SettingType.BOOLEAN,
        default_value = FALSE_STR
    ),

    SettingCode.REDDIT_COMP_NOTIFY: SettingInfo(
        title         = "Receive PM about new competitions",
        validator     = boolean_validator,
        setting_type  = SettingType.BOOLEAN,
        default_value = FALSE_STR
    ),

    SettingCode.USE_CUSTOM_CUBE_COLORS: SettingInfo(
        title         = "Use Custom Cube Colors",
        validator     = boolean_validator,
        setting_type  = SettingType.BOOLEAN,
        default_value = FALSE_STR,
        affects       = [SettingCode.CUSTOM_CUBE_COLOR_B, SettingCode.CUSTOM_CUBE_COLOR_D,
                         SettingCode.CUSTOM_CUBE_COLOR_F, SettingCode.CUSTOM_CUBE_COLOR_L,
                         SettingCode.CUSTOM_CUBE_COLOR_R, SettingCode.CUSTOM_CUBE_COLOR_U]
    ),

    SettingCode.CUSTOM_CUBE_COLOR_U: SettingInfo(
        title         = "U Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_CUBE_COLORS["U"]
    ),

    SettingCode.CUSTOM_CUBE_COLOR_F: SettingInfo(
        title         = "F Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_CUBE_COLORS["F"]
    ),

    SettingCode.CUSTOM_CUBE_COLOR_R: SettingInfo(
        title         = "R Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_CUBE_COLORS["R"]
    ),

    SettingCode.CUSTOM_CUBE_COLOR_D: SettingInfo(
        title         = "D Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_CUBE_COLORS["D"]
    ),

    SettingCode.CUSTOM_CUBE_COLOR_B: SettingInfo(
        title         = "B Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_CUBE_COLORS["B"]
    ),

    SettingCode.CUSTOM_CUBE_COLOR_L: SettingInfo(
        title         = "L Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_CUBE_COLORS["L"]
    ),

    SettingCode.USE_CUSTOM_PYRAMINX_COLORS: SettingInfo(
        title         = "Use Custom Pyraminx Colors",
        validator     = boolean_validator,
        setting_type  = SettingType.BOOLEAN,
        default_value = FALSE_STR,
        affects       = [SettingCode.CUSTOM_PYRAMINX_COLOR_F, SettingCode.CUSTOM_PYRAMINX_COLOR_L,
                         SettingCode.CUSTOM_PYRAMINX_COLOR_R, SettingCode.CUSTOM_PYRAMINX_COLOR_D]
    ),

    SettingCode.CUSTOM_PYRAMINX_COLOR_F: SettingInfo(
        title         = "F Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_PYRA_COLORS["F"]
    ),

    SettingCode.CUSTOM_PYRAMINX_COLOR_L: SettingInfo(
        title         = "L Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_PYRA_COLORS["L"]
    ),

    SettingCode.CUSTOM_PYRAMINX_COLOR_R: SettingInfo(
        title         = "R Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_PYRA_COLORS["R"]
    ),

    SettingCode.CUSTOM_PYRAMINX_COLOR_D: SettingInfo(
        title         = "D Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_PYRA_COLORS["D"]
    ),

    SettingCode.USE_CUSTOM_MEGAMINX_COLORS: SettingInfo(
        title         = "Use Custom Megaminx Colors",
        validator     = boolean_validator,
        setting_type  = SettingType.BOOLEAN,
        default_value = FALSE_STR,
        affects       = [SettingCode.CUSTOM_MEGAMINX_COLOR_1, SettingCode.CUSTOM_MEGAMINX_COLOR_2,
                         SettingCode.CUSTOM_MEGAMINX_COLOR_3, SettingCode.CUSTOM_MEGAMINX_COLOR_4,
                         SettingCode.CUSTOM_MEGAMINX_COLOR_5, SettingCode.CUSTOM_MEGAMINX_COLOR_6,
                         SettingCode.CUSTOM_MEGAMINX_COLOR_7, SettingCode.CUSTOM_MEGAMINX_COLOR_8,
                         SettingCode.CUSTOM_MEGAMINX_COLOR_9, SettingCode.CUSTOM_MEGAMINX_COLOR_10,
                         SettingCode.CUSTOM_MEGAMINX_COLOR_11, SettingCode.CUSTOM_MEGAMINX_COLOR_12]
    ),

    SettingCode.CUSTOM_MEGAMINX_COLOR_1: SettingInfo(
        title         = "Face 1",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_MEGA_COLORS["1"]
    ),

    SettingCode.CUSTOM_MEGAMINX_COLOR_2: SettingInfo(
        title         = "Face 2",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_MEGA_COLORS["2"]
    ),

    SettingCode.CUSTOM_MEGAMINX_COLOR_3: SettingInfo(
        title         = "Face 3",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_MEGA_COLORS["3"]
    ),

    SettingCode.CUSTOM_MEGAMINX_COLOR_4: SettingInfo(
        title         = "Face 4",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_MEGA_COLORS["4"]
    ),

    SettingCode.CUSTOM_MEGAMINX_COLOR_5: SettingInfo(
        title         = "Face 5",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_MEGA_COLORS["5"]
    ),

    SettingCode.CUSTOM_MEGAMINX_COLOR_6: SettingInfo(
        title         = "Face 6",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_MEGA_COLORS["6"]
    ),

    SettingCode.CUSTOM_MEGAMINX_COLOR_7: SettingInfo(
        title         = "Face 7",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_MEGA_COLORS["7"]
    ),

    SettingCode.CUSTOM_MEGAMINX_COLOR_8: SettingInfo(
        title         = "Face 8",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_MEGA_COLORS["8"]
    ),

    SettingCode.CUSTOM_MEGAMINX_COLOR_9: SettingInfo(
        title         = "Face 9",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_MEGA_COLORS["9"]
    ),

    SettingCode.CUSTOM_MEGAMINX_COLOR_10: SettingInfo(
        title         = "Face 10",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_MEGA_COLORS["10"]
    ),

    SettingCode.CUSTOM_MEGAMINX_COLOR_11: SettingInfo(
        title         = "Face 11",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_MEGA_COLORS["11"]
    ),

    SettingCode.CUSTOM_MEGAMINX_COLOR_12: SettingInfo(
        title         = "Face 12",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_MEGA_COLORS["12"]
    ),

    SettingCode.USE_CUSTOM_FTO_COLORS: SettingInfo(
        title         = "Use Custom FTO Colors",
        validator     = boolean_validator,
        setting_type  = SettingType.BOOLEAN,
        default_value = FALSE_STR,
        affects       = [SettingCode.CUSTOM_FTO_COLOR_B, SettingCode.CUSTOM_FTO_COLOR_D,
                         SettingCode.CUSTOM_FTO_COLOR_F, SettingCode.CUSTOM_FTO_COLOR_L,
                         SettingCode.CUSTOM_FTO_COLOR_R, SettingCode.CUSTOM_FTO_COLOR_U,
                         SettingCode.CUSTOM_FTO_COLOR_BL, SettingCode.CUSTOM_FTO_COLOR_BR]
    ),

    SettingCode.CUSTOM_FTO_COLOR_U: SettingInfo(
        title         = "U Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_FTO_COLORS["U"]
    ),

    SettingCode.CUSTOM_FTO_COLOR_R: SettingInfo(
        title         = "R Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_FTO_COLORS["R"]
    ),

    SettingCode.CUSTOM_FTO_COLOR_F: SettingInfo(
        title         = "F Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_FTO_COLORS["F"]
    ),

    SettingCode.CUSTOM_FTO_COLOR_L: SettingInfo(
        title         = "L Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_FTO_COLORS["L"]
    ),

    SettingCode.CUSTOM_FTO_COLOR_B: SettingInfo(
        title         = "B Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_FTO_COLORS["B"]
    ),

    SettingCode.CUSTOM_FTO_COLOR_D: SettingInfo(
        title         = "D Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_FTO_COLORS["D"]
    ),

    SettingCode.CUSTOM_FTO_COLOR_BR: SettingInfo(
        title         = "BR Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_FTO_COLORS["BR"]
    ),

    SettingCode.CUSTOM_FTO_COLOR_BL: SettingInfo(
        title         = "BL Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_FTO_COLORS["BL"]
    ),

    SettingCode.USE_CUSTOM_SQUAN_COLORS: SettingInfo(
        title         = "Use Custom Square-1 Colors",
        validator     = boolean_validator,
        setting_type  = SettingType.BOOLEAN,
        default_value = FALSE_STR,
        affects       = [SettingCode.CUSTOM_SQUAN_COLOR_B, SettingCode.CUSTOM_SQUAN_COLOR_D,
                         SettingCode.CUSTOM_SQUAN_COLOR_F, SettingCode.CUSTOM_SQUAN_COLOR_L,
                         SettingCode.CUSTOM_SQUAN_COLOR_R, SettingCode.CUSTOM_SQUAN_COLOR_U]
    ),

    SettingCode.CUSTOM_SQUAN_COLOR_U: SettingInfo(
        title         = "U Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_SQUAN_COLORS["U"]
    ),

    SettingCode.CUSTOM_SQUAN_COLOR_F: SettingInfo(
        title         = "F Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_SQUAN_COLORS["F"]
    ),

    SettingCode.CUSTOM_SQUAN_COLOR_R: SettingInfo(
        title         = "R Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_SQUAN_COLORS["R"]
    ),

    SettingCode.CUSTOM_SQUAN_COLOR_D: SettingInfo(
        title         = "D Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_SQUAN_COLORS["D"]
    ),

    SettingCode.CUSTOM_SQUAN_COLOR_B: SettingInfo(
        title         = "B Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_SQUAN_COLORS["B"]
    ),

    SettingCode.CUSTOM_SQUAN_COLOR_L: SettingInfo(
        title         = "L Face",
        validator     = hex_color_validator,
        setting_type  = SettingType.HEX_COLOR,
        default_value = DEFAULT_SQUAN_COLORS["L"]
    ),
}

EDIT_TUPLE_FIELDS = ['code', 'title', 'value', 'type', 'affects', 'default', 'opposite_affects']
SettingsEditTuple = namedtuple('SettingsEditTuple', EDIT_TUPLE_FIELDS)

# -------------------------------------------------------------------------------------------------

def __create_unset_setting(user_id, setting_code):
    """ Creates a UserSetting for the specified user and setting code, with a default value. """

    if setting_code not in SETTING_INFO_MAP.keys():
        raise ValueError("That setting doesn't exist!")

    setting_info = SETTING_INFO_MAP[setting_code]
    user_setting  = UserSetting(user_id=user_id, setting_code=setting_code,\
        setting_value=setting_info.default_value)

    DB.session.add(user_setting)
    DB.session.commit()

    return user_setting


def get_default_values_for_settings(setting_codes):
    """ Retrieves the default values for specified setting codes. """

    return { setting_code: SETTING_INFO_MAP[setting_code].default_value \
        for setting_code in setting_codes }


def get_setting_for_user(user_id, setting_code):
    """ Retrieves a user's setting for a given setting code. """

    setting = DB.session.\
        query(UserSetting).\
        filter(UserSetting.user_id == user_id).\
        filter(UserSetting.setting_code == setting_code).\
        first()

    return setting.setting_value if setting \
        else __create_unset_setting(user_id, setting_code).setting_value


def get_boolean_setting_for_user(user_id, setting_code):
    """ Retrieves a boolean setting for the user, and converts it to a bool type. """
    return get_setting_for_user(user_id, setting_code) == TRUE_STR


def get_all_user_ids_with_setting_value(setting_code, setting_value):
    """ Returns a list of all Users' IDs that have the specified setting. """

    matching_settings = DB.session.\
        query(UserSetting).\
        filter(UserSetting.setting_code == setting_code).\
        filter(UserSetting.setting_value == setting_value).\
        all()

    return [s.user_id for s in matching_settings]


def get_bulk_settings_for_user_as_dict(user_id, setting_codes):
    """ Retrieves a dict of code to value for all settings provided. """

    # Retrieve the settings for the specified user and all setting codes provided
    settings = DB.session.\
        query(UserSetting).\
        filter(UserSetting.user_id == user_id).\
        filter(UserSetting.setting_code.in_(setting_codes)).\
        all()

    # If the number of retrieved settings != the number of codes provided, one or more settings
    # haven't been initialized for this user. Create all the missing ones and then retrieve them
    if len(settings) < len(setting_codes):
        __ensure_all_settings_desired_exist(user_id, setting_codes)
        return get_bulk_settings_for_user_as_dict(user_id, setting_codes)

    return { setting.setting_code: setting.setting_value for setting in settings }


def get_settings_for_user_for_edit(user_id, setting_codes):
    """ Retrieves the settings specified in a data format suitable to passing to the front-end
    for editing and viewing. """

    # Retrieve the settings for the specified user and all setting codes provided
    settings = DB.session.\
        query(UserSetting).\
        filter(UserSetting.user_id == user_id).\
        filter(UserSetting.setting_code.in_(setting_codes)).\
        all()

    # If the number of retrieved settings != the number of codes provided, one or more settings
    # haven't been initialized for this user. Create all the missing ones and then retrieve them
    if len(settings) < len(setting_codes):
        __ensure_all_settings_desired_exist(user_id, setting_codes)
        return get_settings_for_user_for_edit(user_id, setting_codes)

    # I know this is terrible in general (O(n^2)), but it's fine for small numbers of settings,
    # and I don't want to implement a real sort key lambda for this right now
    ordered_settings = list()
    for code in setting_codes:
        for setting in settings:
            if setting.setting_code == code:
                ordered_settings.append(setting)
                break

    return [
        SettingsEditTuple(
            code     = setting.setting_code,
            value    = setting.setting_value,
            title    = SETTING_INFO_MAP[setting.setting_code].title,
            affects  = SETTING_INFO_MAP[setting.setting_code].affects,
            type     = SETTING_INFO_MAP[setting.setting_code].setting_type,
            default  = SETTING_INFO_MAP[setting.setting_code].default_value,
            opposite_affects = SETTING_INFO_MAP[setting.setting_code].opposite_affects,
        )
        for setting in ordered_settings
    ]


def set_new_settings_for_user(user_id, settings_dict):
    """ Sets a user's settings for the specified setting codes. """

    for setting_code, setting_value in settings_dict.items():
        setting_info = SETTING_INFO_MAP[setting_code]
        setting_value = setting_info.validator(setting_value)

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


def get_setting_type(setting_code):
    """ Gets the setting type for the specified setting code. """

    return SETTING_INFO_MAP[setting_code].setting_type


def get_color_defaults():
    """ Returns a list of default colors for use in colors swatches. """

    colors = list(DEFAULT_CUBE_COLORS.values())
    colors.extend(DEFAULT_FTO_COLORS.values())

    args = [iter(list(set(colors)))] * 3
    return list(zip_longest(*args, fillvalue=None))


def __ensure_all_settings_desired_exist(user_id, setting_codes):
    """ Iterate through all setting codes and do a dummy retrieval, to make sure the settings
    exist for the user. """

    for code in setting_codes:
        get_setting_for_user(user_id, code)
