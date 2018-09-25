(function() {
    var app = window.app;

    var EVENT_SET_COMPLETE = "event_set_complete";
    var EVENT_SET_INCOMPLETE = "event_set_incomplete";
    var EVENT_SOLVE_RECORD_UPDATED = "event_solve_record_updated";

    function EventsDataManager() {
        app.EventEmitter.call(this);  // EventsDataManager is an EventEmitter

        this.events_data = app.events_data;

        this._setCorrectScrambleStatus();
        this._registerTimerEventHandlers();
    };
    EventsDataManager.prototype = Object.create(app.EventEmitter.prototype);


    /**
     * Iterates over all of the events data at startup and figure out which are complete
     * in-progress/incomplete.
     * 
     * TODO: can we do this on the server-side and just render the template with these classes?
     */
    EventsDataManager.prototype.updateAllEventsStatus = function() {
        $.each(this.events_data, function(i, event){
            this._updateSingleEventStatus(event);
        }.bind(this));
    };

    /**
    * Iterate over all the scrambles for this event, and see if the event is complete
     * or in-progress/incomplete.
     */
    EventsDataManager.prototype._updateSingleEventStatus = function(event) {
        var totalSolves = 0;
        var completeSolves = 0;
        $.each(event.scrambles, function(i, scramble){
            totalSolves += 1;
            if (scramble.time) { completeSolves += 1; }
        });
        if (totalSolves == completeSolves) {
            event.status = 'complete';
            this._recordSummaryForEvent(event);
            this.emit(EVENT_SET_COMPLETE, event.comp_event_id);
        } else if (completeSolves > 0) {
            event.status = 'incomplete';
            this._recordIncompleteSummaryForEvent(event);
            this.emit(EVENT_SET_INCOMPLETE, event.comp_event_id);
        }
    };

    /**
     * Makes a call out to the server to get and save a summary representation for this event
     * Ex: average = (best) (worst) other other other
     */
    EventsDataManager.prototype._recordSummaryForEvent = function(event) {
        var onSummaryComplete = function(data, event) {
            data = JSON.parse(data);
            event.summary = data[event.comp_event_id];
        };
        $.ajax({
            url: "/eventSummaries",
            type: "POST",
            data: JSON.stringify([event]),
            contentType: "application/json",
            success: function(data) { onSummaryComplete(data, event); },
        });
    };

    /**
     * Saves an "in-progress" summary for this event
     * Ex: ? = solve1, solve2, ...
     */
    EventsDataManager.prototype._recordIncompleteSummaryForEvent = function(event) {
        var solves = [];
        $.each(event.scrambles, function(i, scramble) {
            if (scramble.time) {
                var timeStr = "DNF";
                if (!scramble.isDNF) {
                    timeStr = app.convertRawCsForSolveCard(scramble.time, scramble.isPlusTwo);
                }
                solves.push(timeStr);
            }
        });
        event.summary = "? = " + solves.join(", ");
    };

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
     * Returns all of the events data.
     */
    EventsDataManager.prototype.getEventsData = function() {
        return this.events_data;
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
        this._updateSingleEventStatus(this.events_data[compEventId]);

        this.emit(EVENT_SOLVE_RECORD_UPDATED, timerStopData);
    };

    /**
     * Register handlers for timer events.
     */
    EventsDataManager.prototype._registerTimerEventHandlers = function() {
        app.timer.on(app.EVENT_TIMER_STOP, this._updateSolveFromTimerData.bind(this));
    };
  
    // Make EventsDataManager and event names visible at app scope
    app.EventsDataManager = EventsDataManager;
    app.EVENT_SOLVE_RECORD_UPDATED = EVENT_SOLVE_RECORD_UPDATED;
    app.EVENT_SET_COMPLETE = EVENT_SET_COMPLETE;
    app.EVENT_SET_INCOMPLETE = EVENT_SET_INCOMPLETE;
})();