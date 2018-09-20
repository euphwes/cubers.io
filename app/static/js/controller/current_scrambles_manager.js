(function() {

    /**
     * Manages the solves for the currently-active event
     */
    function CurrentScramblesManager() {
        this._registerTimerEventHandlers();
    };

    /**
     * Event handler for when the timer stops - advance the currently attached scrammble to the next one.
     */
    CurrentScramblesManager.prototype._advanceToNextScramble = function() {
        console.log("_advanceToNextScramble");

        // if there are no more incomplete solves, bail out early without doing anything
        var $incompletes = $('.single-time:not(.complete)');
        if ($incompletes.length === 0) { return; }

        // otherwise attach the timer to the first incomplete solve
        var $firstIncomplete = $incompletes.first();
        window.app.timer.attachToScramble(parseInt($firstIncomplete.attr("data-id")));
    };

    /**
     * Register handlers for timer events.
     */
    CurrentScramblesManager.prototype._registerTimerEventHandlers = function() {
        var app = window.app;
        app.timer.on(app.EVENT_TIMER_STOP, this._advanceToNextScramble.bind(this));
    };

    window.app.CurrentScramblesManager = CurrentScramblesManager;
})();