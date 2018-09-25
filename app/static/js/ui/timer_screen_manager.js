(function() {
    var app = window.app;

    function TimerScreenManager() {
        this.$timerDiv = $('#timer_panel');
        this.timerPanelTemplate = Handlebars.compile($('#timer-template').html());

        this._registerAppModeManagerListeners();
    };

    /**
     * Hides the timer screen.
     */
    TimerScreenManager.prototype._hideTimerScreen = function() {
        this.$timerDiv.ultraHide();
    };

    /**
     * Shows the timer screen for the specified event.
     */
    TimerScreenManager.prototype._showTimerScreen = function($selected_event) {
        var events = app.eventsDataManager.getEventsData();
        var comp_event_id = $selected_event.data('comp_event_id');
        var data = {
            comp_event_id : comp_event_id,
            event_id      : $selected_event.data('event_id'),
            event_name    : $selected_event.data('event_name'),
            scrambles     : events[comp_event_id]['scrambles'],
            total_solves  : events[comp_event_id]['scrambles'].length,
            comment       : events[comp_event_id].comment,
        };

        // FMC requires manual entry of integer times, and no timer
        // Gotta do something completely different
        if (data.event_name === 'FMC') {
            data.isFMC = true;
            this._show_entry_for_fmc(data);
            return
        }
        
        // Render the Handlebars tempalte for the timer panel with the event-related data
        // collected above, and set it as the new html for the timer panel div
        this.$timerDiv.html($(this.timerPanelTemplate(data)));
        this.$timerDiv.ultraShow();

        // Determine the first solve/scramble that should be attached to the timer,
        // set it as active, and attach it. If all solves are already complete (because
        // the user is returning to this event after completing them, for whatever reason)
        // then don't attach the timer. Otherwise, choose the first incomplete solve.
        if ($('.single-time:not(.complete)').length != 0) {
            var $firstSolveToAttach = $('.single-time:not(.complete)').first();
            app.timer.attachToScramble(parseInt($firstSolveToAttach.attr("data-id")));
            app.timer.setCompEventId(comp_event_id);
        }
        
        // Adjust the font size for the current scramble to make sure it's as large
        // as possible and still fits in the scramble area
        fitty('.scramble-wrapper>div', {minSize: 18, maxSize: 24});

        app.appModeManager.wire_return_to_events_from_timer();
        this._wire_solve_context_menu();
    };

    /**
     * Show the timer screen, with logic specifically for the FMC event.
     */
    TimerScreenManager.prototype._show_entry_for_fmc = function(data) {
        // Render the Handlebars tempalte for the timer panel with the event-related data
        // collected above, and set it as the new html for the timer panel div
        this.$timerDiv.html($(this.timerPanelTemplate(data)));
        this.$timerDiv.ultraShow();

        // Adjust the font size for the current scramble to make sure it's as large
        // as possible and still fits in the scramble area
        fitty('.scramble-wrapper>div', {minSize: 18, maxSize: 24});

        // swallow tab key, prevent tabbing into next contenteditable div
        $(".single-time.fmc>.time-value").keydown(function (e) {
            var code = (e.keyCode ? e.keyCode : e.which);
            if (code == 9) {
                e.preventDefault();
                return;
            }
        });

        // integers only, and update complete status and raw "time" attribute
        $(".single-time.fmc>.time-value").on("keypress keyup blur",function (e) {
            $(this).val($(this).text().replace(/[^\d].+/, ""));
            if (parseInt($(this).text()) > 0) {
                $(this).parent().addClass('complete');
                $(this).parent().attr("data-rawTimeCentiseconds", parseInt($(this).text() * 100));
            } else {
                $(this).parent().removeClass('complete'); 
                $(this).parent().attr("data-rawTimeCentiseconds", null);
            }
            if ((e.which < 48 || e.which > 57)) {
                e.preventDefault();
            }
        });

        $(".single-time.fmc").click(function(){

            $('.single-time.active').removeClass('active');
            $(this).addClass('active');

            var newScramble = $(this).data('scramble');

            var renderedScramble = "";
            $.each(newScramble.split('\n'), function(i, piece){
                renderedScramble += "<p>" + piece + "</p>";
            });

            var $scrambleHolder = $('.scramble-wrapper>div');
            $scrambleHolder.html(renderedScramble);
        });

        app.appModeManager.wire_return_to_events_from_timer();
    };

    /**
     * Wire up the left-click context menu on each solve card for adding and removing
     * solve penalties (DNF, +2), and retrying a solve.
     */
    TimerScreenManager.prototype._wire_solve_context_menu = function() {
        // Clear all the penalties, set visible time back to the time of the solve
        var clearPenalty = function($solveClicked) {
            $solveClicked.attr('data-isPlusTwo', 'false');
            $solveClicked.attr('data-isDNF', 'false');

            var cs = parseInt($solveClicked.attr("data-rawTimeCentiseconds"));
            $solveClicked.find('.time-value').html(app.convertRawCsForSolveCard(cs));
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
            $solveClicked.find('.time-value').html(app.convertRawCsForSolveCard(cs + 200) + "+");
        }

        // Check if the selected solve is complete
        var isComplete = function($solveClicked) { return $solveClicked.hasClass('complete'); }

        // Check if the selected solve has DNF penalty
        var hasDNF = function($solveClicked) { return app.evaluateBool($solveClicked.attr('data-isDNF')); }

        // Check if the selected solve has +2 penalty
        var hasPlusTwo = function($solveClicked) { return app.evaluateBool($solveClicked.attr('data-isPlusTwo')); }     

        // Retry the selected solve - set it as the only active solve, attach the timer, prepare the timer
        var retrySolve = function($solveClicked) {
            // Remove active status from whichever solve is currently active, if any.
            // Set the selected solve as active.
            $('.single-time.active').removeClass('active');
            $solveClicked.addClass('active');

            // Reset the timer, and attach it to this solve card
            app.timer.reset();
            app.timer.attachToScramble(parseInt($solveClicked.attr("data-id")));
        }

        $.contextMenu({
            selector: '.single-time:not(.fmc)',
            trigger: 'left',
            hideOnSecondTrigger: true,
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
     * Register handlers for EventsDataManager events.
     */
    TimerScreenManager.prototype._registerAppModeManagerListeners = function() {
        app.appModeManager.on(app.EVENT_APP_MODE_TO_TIMER, this._showTimerScreen.bind(this));
        app.appModeManager.on(app.EVENT_APP_MODE_TO_MAIN, this._hideTimerScreen.bind(this));
    };

    app.TimerScreenManager = TimerScreenManager;
})();