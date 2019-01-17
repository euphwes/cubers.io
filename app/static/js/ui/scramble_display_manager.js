(function() {
    var app = window.app;

    /**
     * Manages the scramble display
     */
    function ScrambleDisplayManager() {
        this._registerCurrentScramblesManagerHandlers();
        this._registerEventsDataManagerHandlers();
        this._wireResizeHandler();
    }

    /**
     * Wire up a listener for window resizes that refits the scramble text to the container for the new
     * window size.
     */
    ScrambleDisplayManager.prototype._wireResizeHandler = function() {
        $(window).on('resize', function(){
            textFit($('.scramble-wrapper .scram'), {multiLine: true, maxFontSize: 50});
        });
    };

    /**
     * Event handler for when a scramble is attached to the timer. Show the scramble in the display.
     */
    ScrambleDisplayManager.prototype._showScramble = function(eventData) {
        var rendered = eventData.scramble.scramble.split('\n').join('<br/>');
        $('.scramble-wrapper .scram').html(rendered);
        textFit($('.scramble-wrapper .scram'), {multiLine: true, maxFontSize: 50});
    };

    /**
     * Event handler for when there are no incomplete solves/scrambles left to attach.
     */
    ScrambleDisplayManager.prototype._showDone = function(comp_event_id) {

        comp_event_id = parseInt(comp_event_id);

        // If the event isn't complete, leave early and don't show the done message
        var data = app.eventsDataManager.getDataForEvent(comp_event_id);
        if (data.status != 'complete') { return; }

        // If the event result still is empty, we haven't gotten the result back from the server.
        // Return early, and when the saveEvent call finishes, this will be called again
        if (!Boolean(data.result)) { return; }

        var start = (data.wasPbSingle || data.wasPbAverage) ? "Wow!" : "Congrats!";

        var text = start + "<br/>You've finished " + data.name + " with ";

        if (data.wasPbSingle && data.wasPbAverage) {
            text += "a PB single of " + data.single + " and a PB average of " + data.average + "!";
        } else if (data.wasPbAverage) {
            text += "a PB average of " + data.average + "!";
        } else if (data.wasPbSingle) {
            text += "a PB single of " + data.single + "!";
        } else {
            var eventFormatResultTypeMap = {
                'Bo3': 'a best single of ',
                'Bo1': 'a result of ',
                'Ao5': 'an average of ',
                'Mo3': 'a mean of ',
            };
            text += eventFormatResultTypeMap[data.event_format] + data.result + ".";
        }

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

    /**
     * Register handlers for events data manager events.
     */
    ScrambleDisplayManager.prototype._registerEventsDataManagerHandlers = function() {
        app.eventsDataManager.on(app.EVENT_SUMMARY_CHANGE, this._showDone.bind(this));
    };

    // Make ScrambleDisplayManager visible at app scope
    app.ScrambleDisplayManager = ScrambleDisplayManager;
})();