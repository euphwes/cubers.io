(function() {
    var app = window.app;

    function MainScreenManager() {
        this.$mainScreenDiv = $('#event_list_panel');

        this._registerEventsDataManagerListeners();
        this._registerAppModeManagerListeners();
    };

    /**
     * Get a jQuery reference to the event card for the specified competition event ID.
     */
    MainScreenManager.prototype._getEventCardElementForCompEventId = function(compEventId) {
        return $('#event-' + compEventId);
    };

    /**
     * Sets the card for the specified competition event ID to 'complete'
     */
    MainScreenManager.prototype._setEventCardComplete = function(compEventId) {
        this._getEventCardElementForCompEventId(compEventId)
            .removeClass('incomplete')
            .addClass('complete');
    };

    /**
     * Sets the card for the specified competition event ID to 'incomplete'
     */
    MainScreenManager.prototype._setEventCardIncomplete = function(compEventId) {
        this._getEventCardElementForCompEventId(compEventId)
            .removeClass('complete')
            .addClass('incomplete');
    };

    /**
     * Hides the main screen.
     */
    MainScreenManager.prototype._hideMainScreen = function() {
        this.$mainScreenDiv.ultraHide();
    };

    /**
     * Shows the main screen.
     */
    MainScreenManager.prototype._showTimerScreen = function() {
        this.$mainScreenDiv.ultraShow();
    };

    /**
     * Register handlers for EventsDataManager events.
     */
    MainScreenManager.prototype._registerAppModeManagerListeners = function() {
        app.appModeManager.on(app.EVENT_APP_MODE_TO_MAIN, this._showTimerScreen.bind(this));
        app.appModeManager.on(app.EVENT_APP_MODE_TO_TIMER, this._hideMainScreen.bind(this));
        app.appModeManager.on(app.EVENT_APP_MODE_TO_SUMMARY, this._hideMainScreen.bind(this));
    };

    /**
     * Register handlers for EventsDataManager events.
     */
    MainScreenManager.prototype._registerEventsDataManagerListeners = function() {
        app.eventsDataManager.on(app.EVENT_SET_COMPLETE, this._setEventCardComplete.bind(this));
        app.eventsDataManager.on(app.EVENT_SET_INCOMPLETE, this._setEventCardIncomplete.bind(this));
    };

    app.MainScreenManager = MainScreenManager;
})();