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
        var events = app.eventsDataManager.getEventsData();

        $.each(events, function(i, event){
            if (event.status === 'complete') {
                completeEvents.push(event);
            } else if (event.status === 'incomplete') {
                incompleteEvents.push(event);
            }
        });

        $.ajax({
            url: "/eventSummaries",
            type: "POST",
            data: JSON.stringify(completeEvents),
            contentType: "application/json",
            success: function(data) {
                data = JSON.parse(data);
                this._showSummaryScreen.bind(this)(data, completeEvents, incompleteEvents);
            }.bind(this),
        });
    };

    /**
     * 
     */
    SummaryScreenManager.prototype._showSummaryScreen = function(summary_data, complete_events, incomplete_events) {
        $.each(complete_events, function(i, event) {
            event.summary = summary_data[event.comp_event_id];
        });

        $.each(incomplete_events, function(i, event) {
            var solves = [];
            $.each(event.scrambles, function(i, scramble) {
                if (scramble.time) {
                    var timeStr = "DNF";
                    if (!scramble.isDNF) {
                        timeStr = window.app.convertRawCsForSolveCard(scramble.time, scramble.isPlusTwo);
                    } 
                    solves.push(timeStr);
                }
            });
            event.summary = "? = " + solves.join(", ");
        });

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