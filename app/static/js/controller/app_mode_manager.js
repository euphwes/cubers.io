(function() {
    var app = window.app;

    var EVENT_APP_MODE_TO_MAIN = 'event_app_mode_to_main';
    var EVENT_APP_MODE_TO_TIMER = 'event_app_mode_to_timer';
    var EVENT_APP_MODE_TO_SUMMARY = 'event_app_mode_to_summary';

    function AppModeManager() {
        app.EventEmitter.call(this);  // AppModeManager is an EventEmitter

        this._wire_event_card_click();
        this._wire_review_button();

        this._registerHandlebarsHelpers();
    };
    AppModeManager.prototype = Object.create(app.EventEmitter.prototype);

    /**
     * When clicking on an event card, shows the timer panel for the selected event
     */
    AppModeManager.prototype._wire_event_card_click = function() {
        $('.event-card').click(function(e) {
            var $event = $(e.target).closest('.event-card');
            this.emit(EVENT_APP_MODE_TO_TIMER, $event);
        }.bind(this));
    };

    /**
     * When clicking the review solves button, go to the summary page
     */
    AppModeManager.prototype._wire_review_button = function() {
        $('#times-submit>.btn-summary').click(function() {
            this.emit(EVENT_APP_MODE_TO_SUMMARY);
        }.bind(this));
    };

    /**
     * When clicking the button to return to the events panel, show the main panel
     * and hide the others
     */
    AppModeManager.prototype.wire_return_to_events_from_timer = function() {
        $('#return-to-events>.btn-return').click(function(){
            this.emit(EVENT_APP_MODE_TO_MAIN);
            // FINDME comment
            //var comment = $('#comment_'+compEventId).val();
            //_this.events[compEventId].comment = comment;
        }.bind(this));
    },

    /**
     * 
     */
    AppModeManager.prototype._wire_return_to_events_from_summary = function() {
        $('#summary-buttons>.btn-return').click(function(){
            this.emit(EVENT_APP_MODE_TO_MAIN);
        }.bind(this));
    };

    /**
     * Register Handlebars.js helper functions
     */
    AppModeManager.prototype._registerHandlebarsHelpers = function() {
        // inc: increments the supplied integer by 1
        Handlebars.registerHelper("inc", function(value, options){ return parseInt(value) + 1; });

        // eq: compares two values for equality
        Handlebars.registerHelper("eq", function(a, b, options){ return a == b; });

        // renderTime: returns a user-friendly representation of the supplied centiseconds
        Handlebars.registerHelper("renderTime", window.app.renderTime);

        // General-purpose handlebars helper for performing mathematical operations.
        Handlebars.registerHelper("math", function(lvalue, operator, rvalue, options) {
            if (arguments.length < 4) {
                // Operator omitted, assuming "+"
                options = rvalue;
                rvalue = operator;
                operator = "+";
            }

            lvalue = parseFloat(lvalue);
            rvalue = parseFloat(rvalue);

            return {
                "+": lvalue + rvalue,
                "-": lvalue - rvalue,
                "*": lvalue * rvalue,
                "/": lvalue / rvalue,
                "%": lvalue % rvalue
            }[operator];
        });

        // Converts the value coming in to an integer, then returns the string representation
        Handlebars.registerHelper("int_str", function(value, options){ return "" + parseInt(value); });
    };

    app.AppModeManager = AppModeManager;
    app.EVENT_APP_MODE_TO_MAIN = EVENT_APP_MODE_TO_MAIN;
    app.EVENT_APP_MODE_TO_TIMER = EVENT_APP_MODE_TO_TIMER;
    app.EVENT_APP_MODE_TO_SUMMARY = EVENT_APP_MODE_TO_SUMMARY;
})();