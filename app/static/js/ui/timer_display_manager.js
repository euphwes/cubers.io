(function() {

    /**
     * Manages the state of the visible timer
     */
    function TimerDisplayManager() {
        this._registerTimerEventHandlers();
    };

    /**
     * Event handler for the timer's start event - gets rid of the start "hit spacebar"
     */
    TimerDisplayManager.prototype._updateCardWithTime = function(timerStopData) {
        var $solveCard = this._getSolveCardElement(timerStopData.scrambleId);

        // mark the attached solve card as complete and no longer active
        $solveCard.addClass('complete').removeClass('active');

        // set the visible solve time on the card, and set the data attribute for raw time in centiseconds
        $solveCard.find('.time-value').html(timerStopData.friendlyTimeFull);
        $solveCard.attr("data-rawTimeCentiseconds", timerStopData.rawTimeCs)
        $solveCard.attr("data-isPlusTwo", "false")
        $solveCard.attr("data-isDNF", "false")
    };

    /**
     * Register handlers for timer events.
     */
    TimerDisplayManager.prototype._registerTimerEventHandlers = function() {
        var app = window.app;
        app.timer.on(app.EVENT_TIMER_STOP, this._handleTimerStop.bind(this));
        app.timer.on(app.EVENT_TIMER_START, this._handleTimerStart.bind(this));
        app.timer.on(app.EVENT_TIMER_INTERVAL, this._handleTimerInterval.bind(this));
    };

    window.app.TimerDisplayManager = TimerDisplayManager;
})();