$(function(){

// ---------------------------------------------------------------------------------------------------------------------
// Below is utility code
// ---------------------------------------------------------------------------------------------------------------------
    
    /**
     * Converts an integer number of seconds into a string denoting minutes and seconds.
     * Ex: 120 --> 2:00
     *      90 --> 1:30
     *      65 --> 1:05
     *      51 -->   51
     *       9 -->    9
     */
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
    
    /**
     * Converts an integer number of centiseconds to a string representing the
     * time in minutes, seconds, and centiseconds for use in a timer panel solve card.
     *
     * Ex: 1234 -->   12.34
     *      600 -->    6.00
     *     7501 --> 1:15.01
     *    13022 --> 2:10.22
     */
    var convertRawCsForSolveCard = function(value, plusTwo=false){
        var cs = parseInt(value);
        if (plusTwo) { cs += 200; }

        var s = Math.floor(cs / 100);
        var remainingCs = cs % 100;
        return "" + convertSecondsToMinutes(s) + "." + ("" + remainingCs).padStart(2, "0");
    }

    /**
     * Converts a string to a boolean based on the value of the string, not the presence of the string.
     *
     * Ex: "0" --> false
     *     "1" --> true
     *  "true" --> true
     *  "TRUE" --> true
     * "false" --> false
     * "FALSE" --> false
     */
    var evaluateBool = function(val) {
        return !!JSON.parse(String(val).toLowerCase());
    }

    /**
     * Renders a solve time as a human-friendly string, based on penalty status and raw solve time
     */
    var renderTime = function(solve) {
        if (solve.isDNF) {
            return "DNF";
        }
        if (solve.isPlusTwo) {
            return convertRawCsForSolveCard(solve.time, true) + "+";
        }
        return convertRawCsForSolveCard(solve.time);
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
        this.$singleSolveTimeElem.addClass('active');
        var newScramble = this.$singleSolveTimeElem.data('scramble');

        var $scrambleHolder = $('.scramble-wrapper>span');

        if ($scrambleHolder.text().length === 0) {
            // If there's nothing in the scramble div, this is the first time we're
            // placing something in there, so just put it right in
            
            $scrambleHolder.text(newScramble);
        } else {
            // If there's something already there, we're moving from one scramble
            // to another. Fade the old one out, replace it, and fade the new one in,
            // so the transition isn't as jarring if the scramble length is sufficiently
            // different to make the text visibly jump
        
            $scrambleHolder.fadeOut(100, function() {
                $(this).text(newScramble).delay(100).fadeIn(100);
            });
        }
    };
 
    /**
     * Starts the timer. Captures the start time so we can determine elapsed time on
     * subsequent ticks.
     */
    Timer.prototype.start = function() {
        this.startTime = new Date();
        this.timerInterval = setInterval(this.timerIntervalFunction.bind(this), 10);
    };

    /**
     * Stops the timer, determines the elapsed time, and updates the attached solve element
     * with a user-friendly representation of the elapsed time. Also marks the solve complete,
     * and sets the data attribute for raw time in centiseconds.
     */
    Timer.prototype.stop = function() {
    
        // stop the recurring tick function which continuously updates the timer, and unbind
        // the keyboard space keypress events which handle the timer start/top
        clearInterval(this.timerInterval);
        kd.SPACE.unbindDown(); kd.SPACE.unbindUp();

        // calculate elapsed time, separate seconds and centiseconds, and get the
        // "full time" string as seconds converted to minutes + decimal + centiseconds
        this.elapsedTime = (new Date()) - this.startTime;
        var s = this.elapsedTime.getSecondsFromMs();
        var cs = this.elapsedTime.getTwoDigitCentisecondsFromMs();
        var full_time = convertSecondsToMinutes(s) + "." + cs;

        // mark the attached solve card as complete and no longer active, set the solve time on
        // the card, and set the data attribute for raw time in centiseconds
        this.$singleSolveTimeElem.addClass('complete').removeClass('active');
        this.$singleSolveTimeElem.find('.time-value').html(full_time);
        this.$singleSolveTimeElem.attr("data-rawTimeCentiseconds", parseInt(s*100) + parseInt(cs))
        this.$singleSolveTimeElem.attr("data-isPlusTwo", "false")
        this.$singleSolveTimeElem.attr("data-isDNF", "false")
    };

    /**
     * Resets the timer, clearing start and elapsed time, and sets the visible timer elements
     * to the zero state.
     */
    Timer.prototype.reset = function() {
        clearInterval(this.timerInterval);
        this.startTime = 0;
        this.elapsedTime = 0;
        this.$seconds.html('0');
        this.$centiseconds.html('00');
    };

    /**
     * Checks the current time against the start time to determine
     * elapsed time, and updates the visible timer accordingly.
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
        timer: null,
        timerPanelTemplate: null,
        
        // this is the events_data object that is rendered into the home page template
        events: events_data,  

        /**
         * Wires up the events associated with page elements.
         */
        wire_js_events: function() {
            this.wire_event_card_click();
        },

        /**
         * When clicking on an event card, shows the timer panel for the selected event
         */
        wire_event_card_click: function() {
            $('.event-card').click(function(e) {
                var $event = $(e.target).closest('.event-card');
                this.show_timer_for_event($event);
            }.bind(this));
        },

        /**
         * When clicking the button to return to the events panel, store complete solve times,
         * update the card for the current event to the correct state, then hide the timer panel
         * and show the events panel
         */
        wire_return_to_events: function() {
            var _this = this;
            $('#return-to-events').click(function(e){
                
                // nuke the current timer object, and unbind any bound timer event handlers
                delete _this.timer;
                kd.SPACE.unbindUp(); kd.SPACE.unbindDown();

                var compEventId = $('#timer_panel .timerEventDataContainer').data('compeventid');
                var totalSolves = $('#timer_panel .timerEventDataContainer').data('totalsolves');

                // iterate through each completed solve, grab the scramble ID and raw solve time
                // in centiseconds, and set the solve time for that scramble in the events data object
                $('.single-time.complete').each(function(i){
                    
                    // need to read rawTimeCentiseconds via attr rather than data, since
                    // we create and set that data attribute after the DOM was built
                    var solveCs = parseInt($(this).attr("data-rawTimeCentiseconds"));
                    var isDNF = evaluateBool($(this).attr("data-isDNF"));
                    var isPlusTwo = evaluateBool($(this).attr("data-isPlusTwo"));
                    var scrambleId = $(this).data('id');

                    $.each(_this.events[compEventId].scrambles, function(j, currScramble) {
                        if( currScramble.id != scrambleId ){ return true; }
                        currScramble.time = solveCs;
                        currScramble.isDNF = isDNF;
                        currScramble.isPlusTwo = isPlusTwo;
                        return false;
                    })
                });

                // hide the timer panel and show the events panel
                var $timerDiv  = $('#timer_panel');
                var $eventsDiv = $('#event_list_panel');
                $timerDiv.ultraHide(); $eventsDiv.ultraShow();

                // if the number of complete solves matches the total number of scrambles
                // for this event, mark it as complete
                var completedSolves = $('.single-time.complete').length;
                if (completedSolves == totalSolves) {
                    $('#event-'+compEventId).removeClass('incomplete').addClass('complete');
                } else if (completedSolves > 0) {
                    $('#event-'+compEventId).removeClass('complete').addClass('incomplete');
                } else {
                    $('#event-'+compEventId).removeClass('complete incomplete');
                }
            });
        },

        /**
         * Aggregate all the necessary event-related data, use it to render a new timer panel,
         * and then hide the events panel and show the timer panel
         */
        show_timer_for_event: function($selected_event) {
            var comp_event_id = $selected_event.data('comp_event_id');
            var data = {
                comp_event_id : comp_event_id,
                event_id      : $selected_event.data('event_id'),
                event_name    : $selected_event.data('event_name'),
                scrambles     : this.events[comp_event_id]['scrambles'],
                total_solves   : this.events[comp_event_id]['scrambles'].length,
            };
            
            var $timerDiv  = $('#timer_panel');
            var $eventsDiv = $('#event_list_panel');

            // Render the Handlebars tempalte for the timer panel with the event-related data
            // collected above, and set it as the new html for the timer panel div
            $timerDiv.html($(this.timerPanelTemplate(data)));
            
            // Hide the events panel and show the timer panel
            $eventsDiv.ultraHide(); $timerDiv.ultraShow();

            // Create the new timer object for this timer panel for selected event
            this.timer = new Timer(data.event_name, data.comp_event_id);

            // Determine the first solve/scramble that should be attached to the timer,
            // set it as active, and attach it. If all solves are already complete (because
            // the user is returning to this event after completing them, for whatever reason)
            // then don't attach the timer. Otherwise, choose the first incomplete solve.
            if ($('.single-time:not(.complete)').length != 0) {
                var $firstSolveToAttach = $('.single-time:not(.complete)').first();
                this.timer.attach($firstSolveToAttach);
                this.prepare_timer_for_start();
            }
            
            // Adjust the font size for the current scramble to make sure it's as large
            // as possible and still fits in the scramble area
            fitty('.scramble-wrapper>span', {minSize: 18, maxSize: 45});

            // Wire the solve card and return button events, and get the timer ready to go
            this.wire_return_to_events();
            this.wire_solve_context_menu();
        },

        /**
         * Wire up the left-click context menu on each solve card for adding and removing
         * solve penalties (DNF, +2), and retrying a solve.
         */
        wire_solve_context_menu: function() {
            var _appContext = this;

            // Clear all the penalties, set visible time back to the time of the solve
            var clearPenalty = function($solveClicked) {
                $solveClicked.attr('data-isPlusTwo', 'false');
                $solveClicked.attr('data-isDNF', 'false');

                var cs = parseInt($solveClicked.attr("data-rawTimeCentiseconds"));
                $solveClicked.find('.time-value').html(convertRawCsForSolveCard(cs));
            };

            // Add DNF penalty, set visible time to 'DNF'
            var setDNF = function($solveClicked) {
                $solveClicked.attr('data-isPlusTwo', 'false');
                $solveClicked.attr('data-isDNF', 'true');
                $solveClicked.find('.time-value').html("DNF");
            }

            // Add +2 penalty, set visible time to actual time + 2 seconds, and "+" mark to indicate penalty
            var setPlusTwo = function($solveClicked) {
                $solveClicked.attr('data-isPlusTwo', 'true');
                $solveClicked.attr('data-isDNF', 'false');

                var cs = parseInt($solveClicked.attr("data-rawTimeCentiseconds"));
                $solveClicked.find('.time-value').html(convertRawCsForSolveCard(cs + 200) + "+");
            }

            // Check if the selected solve is complete
            var isComplete = function($solveClicked) { return $solveClicked.hasClass('complete'); }

            // Check if the selected solve has DNF penalty
            var hasDNF = function($solveClicked) { return evaluateBool($solveClicked.attr('data-isDNF')); }

            // Check if the selected solve has +2 penalty
            var hasPlusTwo = function($solveClicked) { return evaluateBool($solveClicked.attr('data-isPlusTwo')); }     

            // Retry the selected solve - set it as the only active solve, attach the timer, prepare the timer
            var retrySolve = function($solveClicked) {
                // Remove active status from whichever solve is currently active, if any.
                // Set the selected solve as active.
                $('.single-time.active').removeClass('active');
                $solveClicked.addClass('active');

                // Reset the timer, and attach it to this solve card
                _appContext.timer.reset();
                _appContext.timer.attach($solveClicked);

                // Wait a beat then attempt to prepare the timer for the user to start it
                setTimeout(_appContext.prepare_timer_for_start.bind(_appContext), 200);
            }

            $.contextMenu({
                selector: '.single-time',
                trigger: 'left',
                items: {
                    "clear": {
                        name: "Clear penalty",
                        icon: "far fa-thumbs-up",
                        callback: function(itemKey, opt, e) { clearPenalty($(opt.$trigger)); },
                        disabled: function(key, opt) { return !(hasDNF(this) || hasPlusTwo(this)); }
                    },
                    "dnf": {
                        name: "DNF",
                        icon: "fas fa-ban",
                        callback: function(itemKey, opt, e) { setDNF($(opt.$trigger)); },
                        disabled: function(key, opt) { return !(isComplete(this) && !hasDNF(this)); }
                    },
                    "+2": {
                        name: "+2",
                        icon: "fas fa-plus",
                        callback: function(itemKey, opt, e) { setPlusTwo($(opt.$trigger)); },
                        disabled: function(key, opt) { return !(isComplete(this) && !hasPlusTwo(this)); }
                    },
                    "sep1": "---------",
                    "retry": {
                        name: "Redo solve",
                        icon: "fas fa-redo",
                        callback: function(itemKey, opt, e) { retrySolve($(opt.$trigger)); },
                        disabled: function(key, opt) { return !isComplete(this) }
                    },
                }
            });
        },

        /**
         * Automatically advances the timer to the next incomplete solve.
         */
        auto_advance_timer_scramble: function() {
            // if there are no more incomplete solves, bail out early without doing anything
            var $incompletes = $('.single-time:not(.complete)');
            if ($incompletes.length === 0) { return; }

            // otherwise attach the timer to the first incomplete solve and prepare the timer
            // to start
            var $firstIncomplete = $incompletes.first();
            this.timer.attach($firstIncomplete);
            setTimeout(this.prepare_timer_for_start.bind(this), 200);
        },

        /**
         * Prepares the timer to start by setting up keyboard events related to starting
         * and stopping the timer.
         */
        prepare_timer_for_start: function() {
        
            // If the spacebar is already down when entering here, that probably means
            // that the user held it after completing the previous solve. Wait for the
            // user to release the spacebar by setting a short timeout to revisit this function
            if (kd.SPACE.isDown()) {
                setTimeout(this.prepare_timer_for_start.bind(this), 200);
                return;
            }
            
            // Pressing the spacebar down "arms" the timer to prepare it to start when
            // the user releases the spacebar
            // TODO: figure out if I need this anymore, now that I'm ensuring the spacebar
            // isn't already down by the time we get here
            var armed = false;
            kd.SPACE.down(function() {
                armed = true;
            });
            
            // When the spacebar is released, unbind the spacebar keydown and keyup events
            // and bind a new keydown event which will stop the timer
            kd.SPACE.up(function() {
            
                // do nothing if the timerisn't armed yet by a spacebar keydown
                if (!armed) { return; }
                
                // unbind the current events
                kd.SPACE.unbindUp(); kd.SPACE.unbindDown();
                
                // start the timer, and bind a new event to spacebar keydown 
                // to stop the timer and then automatically advance to the next scramble
                this.timer.start();
                kd.SPACE.down(function(){
                    this.timer.stop();
                    this.auto_advance_timer_scramble();
                }.bind(this));
            }.bind(this));
        },

        /**
         * Setup stuff when the competition manager app is initialized
         */
        init: function() {
        
            // keydrown.js's keyboard state manager is tick-based
            // this is boilerplate to make sure the kd namespace has a recurring tick
            kd.run(function () { kd.tick(); });

            // wire up all the javascript events we need to handle immediately
            this.wire_js_events();

            // Register Handlebars helper functions to help with rendering timer panel template
            //          inc: increments the supplied integer by 1 and returns
            //           eq: compares two values for equality and returns the result
            // convertRawCs: returns a user-friendly representation of the supplied centiseconds
            Handlebars.registerHelper("inc", function(value, options){ return parseInt(value) + 1; });
            Handlebars.registerHelper("eq", function(a, b, options){ return a == b; });
            Handlebars.registerHelper("renderTime", renderTime);

            // Compile the Handlebars template for the timer panel, and store the renderer
            // so we can render the timer panel later
            this.timerPanelTemplate = Handlebars.compile($('#timer-template').html());
        },
    };

// ---------------------------------------------------------------------------------------------------------------------
// Below is code that's executed on page load, mostly just setup stuff
// ---------------------------------------------------------------------------------------------------------------------

    /**
     * Interpret the number as milliseconds and return the number of
     * whole seconds it represents as a string
     *
     * Ex: 1234 -->  1
     *     2000 -->  2
     *     2001 -->  2
     *    75777 --> 75
     */
    Number.prototype.getSecondsFromMs = function (){
        return ("" + Math.floor(this / 1000));
    };

    /**
     * Interpret the number as milliseconds and return the number of
     * centiseconds remaining after whole seconds are removed, as a string
     * and left-padded with zeros for a total length of 2
     *
     * Ex: 1234 --> 23
     *     2000 --> 00
     *     2001 --> 00
     *    75777 --> 77
     */
    Number.prototype.getTwoDigitCentisecondsFromMs = function (){
        return ("" + this % 1000).slice(0, -1).padStart(2, "0");
    };

    /**
     * Shows or hides the element via the ultra-hidden CSS class.
     * This different than $('thing').hide() or $('thing').show, because that uses `visibility: visible/hidden`
     * which still takes up space, whereas `.ultra-hidden` uses `display: none` which does not take up space
     */
    $.fn.extend({
        ultraHide: function(){ $(this).addClass('ultra-hidden'); },
        ultraShow: function(){ $(this).removeClass('ultra-hidden'); },
    });

    // Let's get this party started!
    CompManagerApp.init();
});