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
        textFit($('.scramble-wrapper .scram'), {multiLine: true, maxFontSize: 50});
    };

    /**
     * Event handler for when there are no incomplete solves/scrambles left to attach.
     */
    ScrambleDisplayManager.prototype._showDone = function(data) {
        var text = "Congrats!<br/>You've finished " + data.event_name + " with ";
        text += data.event_result.result_type + " of " + data.event_result.result + "."

        $('.scramble-wrapper .scram').html(text);
        textFit($('.scramble-wrapper .scram'));
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