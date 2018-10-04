(function() {
    var app = window.app;

    /**
     * Manages the state of the visible timer display based on events emitted by the timer
     */
    function TimerDisplayManager() {
        this._registerTimerEventHandlers();
        this._registerScramblesManagerHandlers();
    };

    /**
     * Displays the specified time on the timer display.
     */
    TimerDisplayManager.prototype._displayTime = function(seconds, centiseconds) {     
        var $dot = $('#dot');
        var $seconds = $('#seconds');
        var $centiseconds = $('#centiseconds');

        $dot.html('.');
        $seconds.html(seconds);
        $centiseconds.html(centiseconds);
    }

    /**
     * Show all zeros.
     */
    TimerDisplayManager.prototype._showZero = function() {     
        this._displayTime("0", "00");
    }

    /**
     * Event handler for the timer's stop event - updates display time
     */
    TimerDisplayManager.prototype._handleTimerStop = function(timerStopData) {
        this._displayTime(timerStopData.friendly_seconds, timerStopData.friendly_centiseconds);
    };

    /**
     * Event handler for the timer's interval event - updates display time
     */
    TimerDisplayManager.prototype._handleTimerInterval = function(intervalData) {
        this._displayTime(intervalData.friendly_seconds, intervalData.friendly_centiseconds);
    };

    /**
     * Register handlers for timer events.
     */
    TimerDisplayManager.prototype._registerTimerEventHandlers = function() {
        app.timer.on(app.EVENT_TIMER_STOP, this._handleTimerStop.bind(this));
        app.timer.on(app.EVENT_TIMER_INTERVAL, this._handleTimerInterval.bind(this));
    };

    /**
     * Register handlers for scrambles manager events.
     */
    TimerDisplayManager.prototype._registerScramblesManagerHandlers = function() {
        app.currentScramblesManager.on(app.EVENT_NOTHING_TO_ATTACH, this._showZero.bind(this));

    };

    app.TimerDisplayManager = TimerDisplayManager;
})();