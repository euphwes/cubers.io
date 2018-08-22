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
        timer: null,
        timerPanelTemplate: null,

        wire_js_events: function() {
            $('.event-card').click(function(e){
                var $event = $(e.target).closest('.event-card');
                this.show_timer_for_event($event);
            }.bind(this));
        },

        show_timer_for_event: function($selected_event) {
            var data = {};
            data.event_id       = $selected_event.data('event_id');
            data.event_name     = $selected_event.data('event_name');
            data.comp_event_id  = $selected_event.data('comp_event_id');
            data.scrambles      = this.events[data.comp_event_id]['scrambles'];
            data.first_scramble = data.scrambles[0].scramble
            
            var $timerDiv  = $('#timer_panel');
            var $eventsDiv = $('#event_list_panel');

            $timerDiv.html($(this.timerPanelTemplate(data)));
            $eventsDiv.ultraHide(); $timerDiv.ultraShow();
        },

        init: function() {
            this.wire_js_events();

            Handlebars.registerHelper("inc", function(value, options){ return parseInt(value) + 1; });
            Handlebars.registerHelper("eq", function(a, b, options){ return a == b; });

            this.timerPanelTemplate = Handlebars.compile($('#timer-template').html());
            //var timer = new Timer("test_event", {});
            //timer.log_name();
        },
    };

// ---------------------------------------------------------------------------------------------------------------------
// Below is code that's executed on page load, mostly just setup stuff
// ---------------------------------------------------------------------------------------------------------------------

    // Utility jQuery functions to "show or hide" based on display: none via ultra-hidden CSS class
    // `visibility: hidden` still takes up space, but `display: none` does not
    $.fn.extend({
        ultraHide: function(){ $(this).addClass('ultra-hidden'); },
        ultraShow: function(){ $(this).removeClass('ultra-hidden'); },
    });

    // Animate.css-related extensions to jQuery, to facilitate applying an animation to an element
    $.fn.extend({
        animateCss: function(animationName, callback) {
          var animationEnd = (function(el) {
            var animations = {
              animation: 'animationend',
              OAnimation: 'oAnimationEnd',
              MozAnimation: 'mozAnimationEnd',
              WebkitAnimation: 'webkitAnimationEnd',
            };
      
            for (var t in animations) {
              if (el.style[t] !== undefined) {
                return animations[t];
              }
            }
          })(document.createElement('div'));
      
          this.addClass('animated ' + animationName).one(animationEnd, function() {
            $(this).removeClass('animated ' + animationName);
      
            if (typeof callback === 'function') callback();
          });
      
          return this;
        },
      });

    CompManagerApp.init();
});