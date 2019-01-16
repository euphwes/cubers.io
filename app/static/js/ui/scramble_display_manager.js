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
    ScrambleDisplayManager.prototype._showDone = function(data) {
        var text = "Congrats!<br/>You've finished " + data.event_name + " with ";
        text += data.event_result.result_type + " of " + data.event_result.result + ".";

        $('.scramble-wrapper .scram').html(text);
        textFit($('.scramble-wrapper .scram'));
    };

    /**
     * Event handler for changing the "congrats you're done!" message if the result changes after
     * this message is already displayed. Due to user adding/removing penalties, manually changing a time, etc
     */
    ScrambleDisplayManager.prototype._possiblyUpdateDoneMessage = function(data) {
        var isShowingDoneMessage = $('.scramble-wrapper .scram').html().indexOf("Congrats!") !== -1;

        if (!isShowingDoneMessage) { return; }

        this._showDone({
            'event_name': app.eventsDataManager.getEventName(data.comp_event_id),
            'event_result': app.eventsDataManager.getEventResult(data.comp_event_id),
        });
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
        app.eventsDataManager.on(app.EVENT_SUMMARY_CHANGE, this._possiblyUpdateDoneMessage.bind(this));
    };

    // Make ScrambleDisplayManager visible at app scope
    app.ScrambleDisplayManager = ScrambleDisplayManager;
})();