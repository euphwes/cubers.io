$(function(){

// ---------------------------------------------------------------------------------------------------------------------
// Below is utility code
// ---------------------------------------------------------------------------------------------------------------------

    var convertSecondsToMinutes = function(seconds) {
        var s = parseFloat(seconds);

        var minutes = Math.floor(s / 60);
        var seconds = s % 60;

        if (minutes > 0) {
            return minutes + ':' + ("" + seconds).padStart(2, "0");
        } else {
            return seconds;
        }
    }

// ---------------------------------------------------------------------------------------------------------------------
// Below is the code related to the timer
// ---------------------------------------------------------------------------------------------------------------------

    /**
     * Represents a timer which records times for a specific competition event.
     */
    var Timer = function(event_name, comp_event_id){
        this.event_name = event_name;
        this.comp_event_id = comp_event_id;

        this.$seconds = $('#seconds');
        this.$centiseconds = $('#centiseconds');
        this.$singleSolveTimeElem = null;

        this.startTime = 0;
        this.elapsedTime = 0;
        this.timerInterval = null;
    };

    /**
     * "Attach" the timer to a specific solve time element so it knows where to store
     * the results when the timer is stopped. 
     */
    Timer.prototype.attach = function(solveTimeElem) {
        this.$singleSolveTimeElem = solveTimeElem;
    }

    /**
     * Starts the timer.
     */
    Timer.prototype.start = function() {
        this.startTime = new Date();
        this.timerInterval = setInterval(this.timerIntervalFunction.bind(this), 10); // In milliseconds
    };

    /**
     * Stops the timer, and sets the timer selement
     */
    Timer.prototype.stop = function() {
        clearInterval(this.timerInterval);
        kd.SPACE.unbindDown();
        kd.SPACE.unbindUp();
        kd.SPACE.unbindPress();

        var now = new Date();
        this.elapsedTime = now - this.startTime;
        var s = this.elapsedTime.getSecondsFromMs();
        var cs = this.elapsedTime.getTwoDigitCentisecondsFromMs();
        var full_time = convertSecondsToMinutes(s) + "." + cs;

        this.$singleSolveTimeElem.addClass('complete');
        this.$singleSolveTimeElem.find('.time-value').html(full_time);
        this.$singleSolveTimeElem.attr("data-rawTimeCentiseconds", parseInt(s*100) + parseInt(cs))
    };

    /**
     * Resets the timer, clearing start and elapsed time, and sets the visible timer elements
     * to the zero state.
     */
    Timer.prototype.reset = function() {
        this.startTime = 0;
        this.elapsedTime = 0;
        clearInterval(this.timerInterval);
        this.$seconds.html('0');
        this.$centiseconds.html('00');
    };

    /**
     * Fires approximately every 10ms, keeps checking current time against start time to determine
     * elapsed time, and updates the visible timer elements accordingly.
     */
    Timer.prototype.timerIntervalFunction = function() {
        var now = new Date();
        var diff = now - this.startTime;
        var s = diff.getSecondsFromMs();
        var cs = diff.getTwoDigitCentisecondsFromMs();

        this.$seconds.html(convertSecondsToMinutes(s));
        this.$centiseconds.html(cs);
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
            var comp_event_id = $selected_event.data('comp_event_id');
            var data = {
                comp_event_id : comp_event_id,
                event_id      : $selected_event.data('event_id'),
                event_name    : $selected_event.data('event_name'),
                scrambles     : this.events[comp_event_id]['scrambles'],
                first_scramble: this.events[comp_event_id]['scrambles'][0].scramble,
            };
            
            var $timerDiv  = $('#timer_panel');
            var $eventsDiv = $('#event_list_panel');

            $timerDiv.html($(this.timerPanelTemplate(data)));
            fitty('.scramble-wrapper>span', {minSize: 18, maxSize: 45});

            $eventsDiv.ultraHide(); $timerDiv.ultraShow();

            this.timer = new Timer(data.event_name, data.comp_event_id);
            this.timer.attach($('.single-time.active'));
            this.prepare_timer_for_start();
        },

        prepare_timer_for_start: function() {
            var spaceDownTime = 0;

            kd.SPACE.down(function () {
                //$('.timer-wrapper').addClass('notReady');
                if (spaceDownTime > 0) {
                    var now = new Date().getTime();
                    if ((now - spaceDownTime) > 100) {
                        //$('.timer-wrapper').removeClass('notReady');
                        $('.timer-wrapper').addClass('ready');
                    }
                    return; 
                }
                spaceDownTime = new Date().getTime();
                this.timer.reset();
            }.bind(this));
        
            kd.SPACE.up(function (e) {
                var x = new Date().getTime() - spaceDownTime;
                spaceDownTime = 0;
                if (x > 100) {
                    kd.SPACE.unbindDown();
                    kd.SPACE.unbindUp();
                    $('.timer-wrapper').removeClass('ready');
                    this.timer.start();
                    kd.SPACE.press(function(){
                        this.timer.stop();
                    }.bind(this));
                } else {
                    //$('.timer-wrapper').removeClass('notReady');
                    this.timer.reset();
                }
            }.bind(this));
        },

        init: function() {
            kd.run(function () { kd.tick(); });

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

    Number.prototype.getSecondsFromMs = function (){
        return ("" + Math.floor(this / 1000));
    };

    Number.prototype.getTwoDigitCentisecondsFromMs = function (){
        return ("" + this % 1000).slice(0, -1).padStart(2, "0");
    };

    // Utility jQuery functions to "show or hide" based on display: none via ultra-hidden CSS class
    // `visibility: hidden` still takes up space, but `display: none` does not
    $.fn.extend({
        ultraHide: function(){ $(this).addClass('ultra-hidden'); },
        ultraShow: function(){ $(this).removeClass('ultra-hidden'); },
    });

    CompManagerApp.init();
});