(function() {
    var app = window.app;

    /**
     * Manages the overall summary page display, and events wired when the page is shown
     */
    function SummaryScreenManager() {
        this.summaryPanelTemplate = Handlebars.compile($('#summary-template').html());
        this._registerAppModeManagerListeners();
    };

    /**
     * Wire up the submit button to submit solve results to the server
     */
    SummaryScreenManager.prototype._wire_submit_button = function() {
        $('#summary-buttons>.btn-submit').click(function(){
            $("#input-results").val(JSON.stringify(app.eventsDataManager.getEventsData()));
            $("#form-results").submit();
        });
    };

    /**
     * Splits the events into a list of complete and incomplete event
     */
    SummaryScreenManager.prototype._splitEventsCompleteIncomplete = function() {
        var complete_events = [];
        var incomplete_events = [];
        $.each(app.eventsDataManager.getEventsData(), function(i, event){
            if (event.status === 'complete') {
                complete_events.push(event);
            } else if (event.status === 'incomplete') {
                incomplete_events.push(event);
            }
        });
        return [complete_events, incomplete_events];
    };

    /**
     * Renders the summmary screen and wires up event handlers
     */
    SummaryScreenManager.prototype._showSummaryScreen = function() {

        var split_events = this._splitEventsCompleteIncomplete();
        var complete_events = split_events[0];
        var incomplete_events = split_events[1];

        var logged_in_with_any_solves = (app.user_logged_in && (complete_events.length > 0 || incomplete_events.length > 0));
        var show_submit_button = (complete_events.length > 0 || logged_in_with_any_solves);

        var data = {
            logged_in: app.user_logged_in,
            comp_title: $('#eventsPanelDataContainer').data('compname'),
            complete_events: complete_events,
            incomplete_events: incomplete_events,
            show_submit_button: show_submit_button,
            no_solves: (complete_events.length == 0 && incomplete_events.length == 0),
        };

        // Render the Handlebars template for the summary panel and display it
        var $summary_div  = $('#summary_panel');
        $summary_div.html($(this.summaryPanelTemplate(data)));
        $summary_div.ultraShow();

        app.appModeManager.wire_return_to_events_from_summary();
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
        app.appModeManager.on(app.EVENT_APP_MODE_TO_SUMMARY, this._showSummaryScreen.bind(this));
        app.appModeManager.on(app.EVENT_APP_MODE_TO_MAIN, this._hideSummaryScreen.bind(this));
    };

    app.SummaryScreenManager = SummaryScreenManager;
})();