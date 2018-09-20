(function() {

    /**
     * Manages the state of the solve cards
     */
    function SolveCardManager() {
        this._registerTimerEvents();
    };

    /**
     * Returns a jQuery refereence to the solve card for the specified scramble ID.
     */
    SolveCardManager.prototype._getSolveCardElement = function(scrambleId) {
        return $('#scramble_' + scrambleId);
    };

    /**
     * Event handler for the timer's stop event - updates the solve cards
     * with the correct time
     */
    SolveCardManager.prototype._updateCardWithTime = function(timerStopData) {
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
    SolveCardManager.prototype._registerTimerEvents = function() {
        var app = window.app;
        app.timer.on(app.EVENT_TIMER_STOP, this._updateCardWithTime.bind(this));
    };

    window.app.SolveCardManager = SolveCardManager;
})();