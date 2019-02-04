(function() {
    var app = window.app;

    // Constants for accessing settings by code
    // NOTE: these must match the setting codes in settings_manager.py
    Settings = {};
    Settings.USE_INSPECTION_TIME    = 'use_inspection_time';
    Settings.HIDE_INSPECTION_TIME   = 'hide_inspection_time';
    Settings.HIDE_RUNNING_TIMER     = 'hide_running_timer';
    Settings.DEFAULT_TO_MANUAL_TIME = 'manual_time_entry_by_default';

    // Stuff related to custom cube colors
    Settings.USE_CUSTOM_CUBE_COLORS = 'use_custom_cube_colors';
    Settings.CUSTOM_CUBE_COLOR_U    = 'custom_cube_color_U';
    Settings.CUSTOM_CUBE_COLOR_F    = 'custom_cube_color_F';
    Settings.CUSTOM_CUBE_COLOR_R    = 'custom_cube_color_R';
    Settings.CUSTOM_CUBE_COLOR_D    = 'custom_cube_color_D';
    Settings.CUSTOM_CUBE_COLOR_B    = 'custom_cube_color_B';
    Settings.CUSTOM_CUBE_COLOR_L    = 'custom_cube_color_L';

    // Stuff related to custom pyraminx colors
    Settings.USE_CUSTOM_PYRAMINX_COLORS = 'use_custom_pyraminx_colors';
    Settings.CUSTOM_PYRAMINX_COLOR_F    = 'custom_pyra_color_F';
    Settings.CUSTOM_PYRAMINX_COLOR_L    = 'custom_pyra_color_L';
    Settings.CUSTOM_PYRAMINX_COLOR_R    = 'custom_pyra_color_R';
    Settings.CUSTOM_PYRAMINX_COLOR_D    = 'custom_pyra_color_D';

    // Stuff related to custom megaminx colors
    Settings.USE_CUSTOM_MEGAMINX_COLORS = 'use_custom_megaminx_colors'
    Settings.CUSTOM_MEGAMINX_COLOR_1    = 'custom_mega_color_1'
    Settings.CUSTOM_MEGAMINX_COLOR_2    = 'custom_mega_color_2'
    Settings.CUSTOM_MEGAMINX_COLOR_3    = 'custom_mega_color_3'
    Settings.CUSTOM_MEGAMINX_COLOR_4    = 'custom_mega_color_4'
    Settings.CUSTOM_MEGAMINX_COLOR_5    = 'custom_mega_color_5'
    Settings.CUSTOM_MEGAMINX_COLOR_6    = 'custom_mega_color_6'
    Settings.CUSTOM_MEGAMINX_COLOR_7    = 'custom_mega_color_7'
    Settings.CUSTOM_MEGAMINX_COLOR_8    = 'custom_mega_color_8'
    Settings.CUSTOM_MEGAMINX_COLOR_9    = 'custom_mega_color_9'
    Settings.CUSTOM_MEGAMINX_COLOR_10   = 'custom_mega_color_10'
    Settings.CUSTOM_MEGAMINX_COLOR_11   = 'custom_mega_color_11'
    Settings.CUSTOM_MEGAMINX_COLOR_12   = 'custom_mega_color_12'

    /**
     * Manages user settings
     */
    function UserSettingsManager() {
        this.settings_data = app.settings_data;
        this._parse_boolean_settings();
    }

    /**
     * Retrieve the value for the provided setting.
     */
    UserSettingsManager.prototype.get_setting = function(code) {
        var value = this.settings_data[code];
        if (value === undefined) {
            return null;
        } else {
            return value;
        }
    };

    /**
     * Set the value for the provided setting.
     */
    UserSettingsManager.prototype._set_setting = function(code, value) {
        this.settings_data[code] = value;
    };

    /**
     * On page load, parse through all the boolean settings and ensure their values are bools
     * and not strings.
     */
    UserSettingsManager.prototype._parse_boolean_settings = function() {
        // Settings which are known to contain boolean values
        boolean_settings = [
            Settings.USE_INSPECTION_TIME,
            Settings.HIDE_RUNNING_TIMER,
            Settings.HIDE_INSPECTION_TIME,
            Settings.DEFAULT_TO_MANUAL_TIME,
            Settings.USE_CUSTOM_MEGAMINX_COLORS,
            Settings.USE_CUSTOM_PYRAMINX_COLORS,
            Settings.USE_CUSTOM_CUBE_COLORS,
        ];

        $.each(boolean_settings, function(i, code) {
            this.settings_data[code] = this.settings_data[code] == "true" ? true : false;
        }.bind(this));
    };

    // Make UserSettingsManager and setting code constants visible at app scope
    app.UserSettingsManager = UserSettingsManager;
    app.Settings = Settings;
})();