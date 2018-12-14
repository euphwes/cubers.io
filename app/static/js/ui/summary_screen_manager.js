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
     * Splits the events into a list of complete and incomplete event
     */
    SummaryScreenManager.prototype._splitEventsCompleteIncomplete = function() {
        var complete_events = [];
        var incomplete_events = [];
        var event_format_result_type_dict = {
            "Ao5": "Average: ",
            "Mo3": "Mean: ",
            "Bo1": "Best: ",
            "Bo3": "Best: ",
        };
        $.each(app.eventsDataManager.getEventsData(), function(i, event){
            if (event.status === 'complete') {
                if (event.summary.indexOf(" = ") > -1) {
                    event.short_summary = event_format_result_type_dict[event.event_format] + event.summary.substr(0, event.summary.indexOf(" = "));
                } else {
                    event.short_summary = event_format_result_type_dict[event.event_format] + event.summary;
                }
                complete_events.push(event);
            } else if (event.status === 'incomplete') {
                event.short_summary = event.summary.replace("? = ", "");
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

        var data = {
            logged_in: app.user_logged_in,
            comp_title: $('#eventsPanelDataContainer').data('compname'),
            complete_events: complete_events,
            incomplete_events: incomplete_events,
            no_solves: (complete_events.length == 0 && incomplete_events.length == 0),
        };

        // Render the Handlebars template for the summary panel and display it
        var $summary_div  = $('#summary_panel');
        $summary_div.html($(this.summaryPanelTemplate(data)));
        $summary_div.ultraShow();

        app.appModeManager.wire_return_to_events_from_summary();

        if (app.user_logged_in) {
            $.get('/comment_url/' + app.eventsDataManager.getCompId(), function(data) {
                var anchor = $('<a>Check out your results here!</a>').attr("href", data).attr("target", "_blank");
                $('.span_complete').append(anchor);
            })
        }
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