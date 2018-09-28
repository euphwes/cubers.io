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
    SolveCardManager.prototype._getSolveCardElement = function(scramble_id) {
        return $('#scramble_' + scramble_id);
    };

    /**
     * Event handler for the timer's stop event - updates the solve cards
     * with the correct time
     */
    SolveCardManager.prototype._updateCardWithTime = function(event_data) {
        var $solve_card = this._getSolveCardElement(event_data.scramble_id);

        if (event_data.is_delete) {
            // mark the attached solve card as no longer complete
            $solve_card.removeClass('complete');
        } else {
            // mark the attached solve card as complete and no longer active
            $solve_card.addClass('complete').removeClass('active');
        }


        // set the visible solve time on the card
        $solve_card.find('.time-value').html(event_data.friendly_time_full);
    };

    /**
     * Sets only the card for the specified scramble as active.
     */
    SolveCardManager.prototype._setCardAsActive = function(scramble) {
        $('.single-time.active').removeClass('active');
        this._getSolveCardElement(scramble.id).addClass('active');
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