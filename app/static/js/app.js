$(function(){

// ---------------------------------------------------------------------------------------------------------------------
// Below is the code related to the competition manager
// ---------------------------------------------------------------------------------------------------------------------

    /**
     * The application which manages the competition, stores times for all competition events, creates timer instances
     */
    var CompManagerApp = {
        timer: null,
        timerPanelTemplate: null,
        summaryPanelTemplate: null,
        
        // this is the events_data object that is rendered into the home page template
        events: window.app.events_data,  

        wire_submit_button_click: function() {
            var _appContext = this;

            $('#times-submit>.btn-summary').click(function() {
                var completeEvents = [];
                var incompleteEvents = [];
                $.each(this.events, function(i, event){
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
                        _appContext
                            .show_summary_panel.bind(_appContext)(data, completeEvents, incompleteEvents);
                    },
                });
            }.bind(_appContext));
        },

        show_summary_panel: function(summary_data, complete_events, incomplete_events) {
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

            var $summaryDiv  = $('#summary_panel');
            var $eventsDiv = $('#event_list_panel');

            // Render the Handlebars template for the summary panel, and set it as
            // the new html for the summary panel div
            $summaryDiv.html($(this.summaryPanelTemplate(data)));

            // Hide the events panel and show the summary panel
            $eventsDiv.ultraHide(); $summaryDiv.ultraShow();

            this.wire_return_to_events_from_summary();
            this.wire_submit_button();
        },

        /**
         * 
         */
        wire_return_to_events_from_summary: function() {
            $('#summary-buttons>.btn-return').click(function(e){
                // hide the summary panel and show the events panel
                var $summaryDiv  = $('#summary_panel');
                var $eventsDiv = $('#event_list_panel');
                $summaryDiv.ultraHide(); $eventsDiv.ultraShow();
            });
        },

        /**
         * 
         */
        wire_submit_button: function() {
            var _appContext = this;
            $('#summary-buttons>.btn-submit').click(function(e){
                $("#input-results").val(JSON.stringify(_appContext.events));
                $("#form-results").submit();
            });
        },

         /**
         * Setup stuff when the competition manager app is initialized
         */
        init: function() {
            // wire up all the javascript events we need to handle immediately
            this.wire_js_events();
        },
    };

    // Let's get this party started!
    CompManagerApp.init();
});