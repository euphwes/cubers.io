$(function(){

// ---------------------------------------------------------------------------------------------------------------------
// Below is the code related to the timer
// ---------------------------------------------------------------------------------------------------------------------

    /**
     * Represents a timer which records times for a specific competition event.
     * 
     * @constructor
     * @param {string} event_name 
     * @param {object} scrambles_data 
     */
    var Timer = function(event_name, scrambles_data){
        this.event_name = event_name;
        this.scrambles_data = scrambles_data;
    };

    /**
     * Test function for logging the competition event name to the console.
     */
    Timer.prototype.log_name = function() {
        console.log(this.event_name);
    };

// ---------------------------------------------------------------------------------------------------------------------
// Below is the code related to the competition manager
// ---------------------------------------------------------------------------------------------------------------------

    /**
     * The application which manages the competition, stores times for all competition events, creates timer instances
     */
    var CompManagerApp = {
        events: events_data,

        wire_js_events: function() {
            $('.event-card').click(function(){
                $(this).toggleClass('complete');
                $('#times-submit').toggleClass('visible');
            })
        },

        init: function() {
            this.wire_js_events();
            //var timer = new Timer("test_event", {});
            //timer.log_name();
        },
    };

    CompManagerApp.init();
});