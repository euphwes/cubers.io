(function() {

    var EVENT_SOLVE_RECORD_UPDATED = "event_solve_record_updated";

    function EventsDataManager() {
        window.app.EventEmitter.call(this);  // EventsDataManager is an EventEmitter

        this.events_data = window.app.events_data;
        this._setCorrectScrambleStatus();
        this._registerTimerEventHandlers();
    };
    EventsDataManager.prototype = Object.create(window.app.EventEmitter.prototype);

    /**
     * Checks each scramble on load to see if a time is set. If yes, set status to complete,
     * otherwise set status to incomplete.
     */
    EventsDataManager.prototype._setCorrectScrambleStatus = function() {
        $.each(this.events_data, function(i, compEvent) {
            $.each(compEvent.scrambles, function(j, scramble) {
                scramble.status = Boolean(scramble.time) ? 'complete' : 'incomplete';
            });
        });
    };

    /**
     * Gets the next incomplete scramble for the provided competition event ID
     */
    EventsDataManager.prototype.getNextIncompleteScramble = function(compEventId) {
        var nextScramble = null;
        $.each(this.events_data[compEventId].scrambles, function(i, currScramble) {
            if (currScramble.status === 'incomplete') {
                nextScramble = currScramble;
                return false;
            }
        });
        return nextScramble;
    };

    /**
     * Updates a solve in the events data with the elapsed time from the 
     */
    EventsDataManager.prototype._updateSolveFromTimerData = function(timerStopData) {

        var compEventId = timerStopData.compEventId;
        var scrambleId  = timerStopData.scrambleId;

        $.each(this.events_data[compEventId].scrambles, function(i, currScramble) {
            if (currScramble.id != scrambleId) { return true; }

            currScramble.time      = timerStopData.rawTimeCs;
            currScramble.isDNF     = timerStopData.isDNF;
            currScramble.isPlusTwo = timerStopData.isPlusTwo;
            currScramble.status    = "complete";
            return false;
        });

        this.emit(EVENT_SOLVE_RECORD_UPDATED, timerStopData);
    };

    /**
     * Register handlers for timer events.
     */
    EventsDataManager.prototype._registerTimerEventHandlers = function() {
        var app = window.app;
        app.timer.on(app.EVENT_TIMER_STOP, this._updateSolveFromTimerData.bind(this));
    };
  
    // Make EventsDataManager and event names visible at app scope
    window.app.EventsDataManager = EventsDataManager;
    window.app.EVENT_SOLVE_RECORD_UPDATED = EVENT_SOLVE_RECORD_UPDATED;
})();