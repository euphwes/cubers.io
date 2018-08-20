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
        timer: {},

        wire_js_events: function() {
            $('.event-card').click(function(e){
                var $event     = $(e.target).closest('.event-card');
                var event_id   = $event.data('event_id');
                var event_name = $event.data('event_name');
                var scrambles  = this.events[event_id]['scrambles'];

                this.setup_timer_modal_for_event(event_name, scrambles);
                $('#time_entry_modal').modal();
            }.bind(this));
        },

        setup_timer_modal_for_event: function(name, scrambles) {
            $('#time_entry_modal_title').text(name);
            $('#time_entry_modal_scrambles').text(scrambles[0]['scramble']);
        },

        init: function() {
            this.wire_js_events();
            //var timer = new Timer("test_event", {});
            //timer.log_name();
        },
    };

    CompManagerApp.init();
});