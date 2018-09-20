(function() {

    /**
     * Manages the solves for the currently-active event
     */
    function EventSolvesManager() {
        this._registerTimerEventHandlers();
    };

    /**
     * Event handler for when the timer stops - advance the 
     */
    EventSolvesManager.prototype._advanceToNextScramble = function() {
        var app = window.app;
        app.timer.on(app.EVENT_TIMER_STOP, this._advanceToNextScramble.bind(this));
    };

    /**
     * Register handlers for timer events.
     */
    EventSolvesManager.prototype._registerTimerEventHandlers = function() {
        var app = window.app;
        app.timer.on(app.EVENT_TIMER_STOP, this._advanceToNextScramble.bind(this));
    };

    window.app.EventSolvesManager = EventSolvesManager;
})();