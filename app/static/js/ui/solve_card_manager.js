(function() {
    var app = window.app;

    /**
     * Manages the state of the solve cards
     */
    function SolveCardManager() {
        this._registerEventsDataMangerEventHandlers();
        this._registerCurrentScramblesManagerEventHandlers();
    };

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
    };

    /**
     * Event handler for the timer's stop event - updates the solve cards
     * with the correct time
     */
    SolveCardManager.prototype._setCardAsActive = function(scrambleId) {
        this._getSolveCardElement(scrambleId).addClass('complete');
    };

    /**
     * Register handlers for EventsDataManager events.
     */
    SolveCardManager.prototype._registerEventsDataMangerEventHandlers = function() {
        app.eventsDataManager.on(app.EVENT_SOLVE_RECORD_UPDATED, this._updateCardWithTime.bind(this));
    };

    /**
     * Register handlers for CurrentScramblesManager events.
     */
    SolveCardManager.prototype._registerCurrentScramblesManagerEventHandlers = function() {
        app.currentScramblesManager.on(app.EVENT_NEW_SCRAMBLE_ATTACHED, this._setCardAsActive.bind(this));
    };

    app.SolveCardManager = SolveCardManager;
})();