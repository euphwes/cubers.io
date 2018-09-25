(function() {
    var app = window.app;

    function SummaryScreenManager() {
        this.summaryPanelTemplate = Handlebars.compile($('#summary-template').html());
        this._registerAppModeManagerListeners();
    };

    /**
     * 
     */
    SummaryScreenManager.prototype._wire_submit_button = function() {
        $('#summary-buttons>.btn-submit').click(function(){
            $("#input-results").val(JSON.stringify(app.eventsDataManager.getEventsData()));
            $("#form-results").submit();
        });
    };

    /**
     * 
     */
    SummaryScreenManager.prototype._buildSummary = function() {
        var completeEvents = [];
        var incompleteEvents = [];
        $.each(app.eventsDataManager.getEventsData(), function(i, event){
            if (event.status === 'complete') {
                completeEvents.push(event);
            } else if (event.status === 'incomplete') {
                incompleteEvents.push(event);
            }
        });
        this._showSummaryScreen(completeEvents, incompleteEvents);
    };

    /**
     * 
     */
    SummaryScreenManager.prototype._showSummaryScreen = function(complete_events, incomplete_events) {
        var logged_in_with_any_solves = (window.app.user_logged_in && (complete_events.length > 0 || incomplete_events.length > 0));
        var show_submit_button = (complete_events.length > 0 || logged_in_with_any_solves);

        var data = {
            logged_in: window.app.user_logged_in,
            comp_title: $('#eventsPanelDataContainer').data('compname'),
            complete_events: complete_events,
            incomplete_events: incomplete_events,
            show_submit_button: show_submit_button,
            no_solves: (complete_events.length == 0 && incomplete_events.length == 0),
        };

        // Render the Handlebars template for the summary panel and display it
        var $summaryDiv  = $('#summary_panel');
        $summaryDiv.html($(this.summaryPanelTemplate(data)));
        $summaryDiv.ultraShow();

        app.appModeManager._wire_return_to_events_from_summary();
        this._wire_submit_button();
    };

    /**
     * Hides the summary screen
     */
    SummaryScreenManager.prototype._hideSummaryScreen = function() {
        $('#summary_panel').ultraHide();
    };

    /**
     * Register handlers for EventsDataManager events.
     */
    SummaryScreenManager.prototype._registerAppModeManagerListeners = function() {
        app.appModeManager.on(app.EVENT_APP_MODE_TO_SUMMARY, this._buildSummary.bind(this));
        app.appModeManager.on(app.EVENT_APP_MODE_TO_MAIN, this._hideSummaryScreen.bind(this));
    };

    app.SummaryScreenManager = SummaryScreenManager;
})();