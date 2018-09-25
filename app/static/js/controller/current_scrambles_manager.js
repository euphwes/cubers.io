(function() {
    var app = window.app;

    var EVENT_NEW_SCRAMBLE_ATTACHED = "event_new_scramble_attached";

    /**
     * Manages the solves for the currently-active event
     */
    function CurrentScramblesManager() {
        app.EventEmitter.call(this);  // CurrentScramblesManager is an EventEmitter
        this._registerTimerEventHandlers();
    };
    CurrentScramblesManager.prototype = Object.create(app.EventEmitter.prototype);

    /**
     * Event handler for events data gets updated. Advance the timer scramble to the next incomplete one
     * for the current competition event.
     */
    CurrentScramblesManager.prototype._advanceScrambleAfterTimerStop = function(timerStopData) {
        this._attachNextUnsolvedScramble(timerStopData.compEventId);

    };

    /**
     *
     */
    CurrentScramblesManager.prototype.attachFirstScramble = function(compEventId) {
        this._attachNextUnsolvedScramble(compEventId);
    };

    /**
     *
     */
    CurrentScramblesManager.prototype._attachNextUnsolvedScramble = function(compEventId) {
        var nextIncompleteScramble = app.eventsDataManager.getNextIncompleteScramble(compEventId);
        if (nextIncompleteScramble) {
            app.timer.attachToScramble(nextIncompleteScramble.id);
            this.emit(EVENT_NEW_SCRAMBLE_ATTACHED, nextIncompleteScramble);
        }
    };

    /**
     * Register handlers for events data manager events.
     */
    CurrentScramblesManager.prototype._registerTimerEventHandlers = function() {
        app.eventsDataManager.on(app.EVENT_SOLVE_RECORD_UPDATED, this._advanceScrambleAfterTimerStop.bind(this));
    };

    // Make CurrentScramblesManager and event names visible at app scope
    app.CurrentScramblesManager = CurrentScramblesManager;
    app.EVENT_NEW_SCRAMBLE_ATTACHED = EVENT_NEW_SCRAMBLE_ATTACHED;
})();