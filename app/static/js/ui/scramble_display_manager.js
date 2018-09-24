(function() {
    var app = window.app;

    /**
     * Manages the scramble display
     */
    function ScrambleDisplayManager() {
        this._registerCurrentScramblesManagerHandlers();
    };

    /**
     * Event handler for when a scramble is attached to the timer. Show the scramble in the display.
     */
    ScrambleDisplayManager.prototype._showScramble = function(scramble) {
        $('.scramble-wrapper>div').html(scramble.scramble);
    };

    /**
     * Register handlers for current scrambles manager events.
     */
    ScrambleDisplayManager.prototype._registerCurrentScramblesManagerHandlers = function() {
        app.currentScramblesManager.on(app.EVENT_NEW_SCRAMBLE_ATTACHED, this._showScramble.bind(this));
    };

    // Make ScrambleDisplayManager visible at app scope
    app.ScrambleDisplayManager = ScrambleDisplayManager;
})();