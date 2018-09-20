(function() {

    var EVENT_SOLVE_RECORD_UPDATED = "event_solve_record_updated";

    function EventsDataManager() {
        window.app.EventEmitter.call(this);  // EventsDataManager is an EventEmitter

        this.events_data = window.app.events_data;
        console.log("initial data");
        console.log(this.events_data);
        this._registerTimerEventHandlers();
    };
    EventsDataManager.prototype = Object.create(window.app.EventEmitter.prototype);

    /**
     * Updates a solve in the events data with the elapsed time from the 
     */
    EventsDataManager.prototype._updateSolveFromTimerData = function(timerStopData) {

        var compEventId = timerStopData.compEventId;
        var scrambleId  = timerStopData.scrambledId;

        $.each(this.events_data[compEventId].scrambles, function(i, currScramble) {
            if( currScramble.id != scrambleId ){ return true; }

            currScramble.time      = timerStopData.rawTimeCs;
            currScramble.isDNF     = timerStopData.isDNF;
            currScramble.isPlusTwo = timerStopData.isPlusTwo;
            return false;
        });

        this.emit(EVENT_SOLVE_RECORD_UPDATED, timerStopData);
    }

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