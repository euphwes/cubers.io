(function() {

    /**
     * Manages the state of the visible timer
     */
    function TimerDisplayManager() {
        this._registerTimerEventHandlers();
    };

    /**
     * Displays the specified time on the timer display.
     */
    TimerDisplayManager.prototype._displayTime = function(seconds, centiseconds) {     
        var $dot = $('#dot');
        var $seconds = $('#seconds');
        var $centiseconds = $('#centiseconds');

        $dot.html('.');
        $seconds.html(window.app.convertSecondsToMinutes(seconds));
        $centiseconds.html(centiseconds);
    }

    /**
     * Event handler for the timer's stop event - updates display time
     */
    TimerDisplayManager.prototype._handleTimerStop = function(timerStopData) {
        this._displayTime(timerStopData.friendlySeconds, timerStopData.friendlyCentiseconds);
    };

    /**
     * Event handler for the timer's interval event - updates display time
     */
    TimerDisplayManager.prototype._handleTimerInterval = function(intervalData) {
        this._displayTime(intervalData.friendlySeconds, intervalData.friendlyCentiseconds);
    };

    /**
     * Register handlers for timer events.
     */
    TimerDisplayManager.prototype._registerTimerEventHandlers = function() {
        var app = window.app;
        app.timer.on(app.EVENT_TIMER_STOP, this._handleTimerStop.bind(this));
        app.timer.on(app.EVENT_TIMER_INTERVAL, this._handleTimerInterval.bind(this));
    };

    window.app.TimerDisplayManager = TimerDisplayManager;
})();