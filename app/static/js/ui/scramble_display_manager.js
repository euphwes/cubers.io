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
        var rendered = scramble.scramble.split('\n').join('<br/>');
        $('.scramble-wrapper .scram').html(rendered);
    };

    /**
     * Event handler for when there are no incomplete solves/scrambles left to attach.
     */
    ScrambleDisplayManager.prototype._showDone = function(event_name) {
        $('.scramble-wrapper .scram').html("Congrats! You're done with " + event_name + ".");
    };

    /**
     * Register handlers for current scrambles manager events.
     */
    ScrambleDisplayManager.prototype._registerCurrentScramblesManagerHandlers = function() {
        app.currentScramblesManager.on(app.EVENT_NOTHING_TO_ATTACH, this._showDone.bind(this));
        app.currentScramblesManager.on(app.EVENT_NEW_SCRAMBLE_ATTACHED, this._showScramble.bind(this));
    };

    // Make ScrambleDisplayManager visible at app scope
    app.ScrambleDisplayManager = ScrambleDisplayManager;
})();