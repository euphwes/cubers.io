(function() {

    var EVENT_SOLVE_CARDS_UPDATED = "event_solve_cards_updated";

    /**
     * Manages the state of the solve cards
     */
    function SolveCardManager() {
        window.app.EventEmitter.call(this);  // SolveCardManager is an EventEmitter
        this._registerTimerEventHandlers();
    };
    SolveCardManager.prototype = Object.create(window.app.EventEmitter.prototype);

    /**
     * Returns a jQuery reference to the solve card for the specified scramble ID.
     */
    SolveCardManager.prototype._getSolveCardElement = function(scrambleId) {
        return $('#scramble_' + scrambleId);
    };

    /**
     * Event handler for the timer's stop event - updates the solve cards
     * with the correct time
     */
    SolveCardManager.prototype._updateCardWithTime = function(eventData) {
        var $solveCard = this._getSolveCardElement(eventData.scrambleId);

        // mark the attached solve card as complete and no longer active
        $solveCard.addClass('complete').removeClass('active');

        // set the visible solve time on the card
        $solveCard.find('.time-value').html(eventData.friendlyTimeFull);

        this.emit(EVENT_SOLVE_CARDS_UPDATED);
    };

    /**
     * Register handlers for timer events.
     */
    SolveCardManager.prototype._registerTimerEventHandlers = function() {
        var app = window.app;
        app.eventsDataManager.on(app.EVENT_SOLVE_RECORD_UPDATED, this._updateCardWithTime.bind(this));
    };

    window.app.SolveCardManager = SolveCardManager;
    window.app.EVENT_SOLVE_CARDS_UPDATED = EVENT_SOLVE_CARDS_UPDATED;
})();