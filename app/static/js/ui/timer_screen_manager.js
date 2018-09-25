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
        data.isFMC = data.event_name === 'FMC';

        // Render the Handlebars template for the timer panel with the event-related data
        // collected above, and set it as the new html for the timer panel div
        this.$timerDiv.html($(this.timerPanelTemplate(data)));
        this.$timerDiv.ultraShow();

        // Adjust the font size for the current scramble to make sure it's as large
        // as possible and still fits in the scramble area
        fitty('.scramble-wrapper>div', {minSize: 18, maxSize: 24});

        app.timer.setCompEventId(comp_event_id);
        app.currentScramblesManager.attachFirstScramble(comp_event_id);

        app.appModeManager.wire_return_to_events_from_timer();
        this._wire_comment_box();

        if (data.isFMC) {
            this._wire_FMC_solve_cards();
        } else {
            this._wire_solve_context_menu(comp_event_id);
        }
    };

    /**
     * Wire up the comment box to save the comment to the events data when done typing.
     */
    TimerScreenManager.prototype._wire_comment_box = function(comp_event_id) {
        var commentTimeout = null;
        var $comment = $('#comment_' + comp_event_id);
        $comment.keyup(function(){
            clearTimeout(commentTimeout);
            commentTimeout = setTimeout(function(){
                app.eventsDataManager.setCommentForEvent($comment.val(), comp_event_id);
            }, 500);
        });
    };

    /**
     * Show the timer screen, with logic specifically for the FMC event.
     * TODO note this is a little hackish and calls events_data_manager stuff directly
     * rather than using timer events (since there is no timer)
     */
    TimerScreenManager.prototype._wire_FMC_solve_cards = function() {
        // Swallow tab key, prevent tabbing into next contenteditable div
        $(".single-time.fmc>.time-value").keydown(function (e) {
            var code = (e.keyCode ? e.keyCode : e.which);
            if (code == 9) {
                e.preventDefault();
                return;
            }
        });
        
        /**
         *        var compEventId = timerStopData.compEventId;
        var scrambleId  = timerStopData.scrambleId;

        $.each(this.events_data[compEventId].scrambles, function(i, currScramble) {
            if (currScramble.id != scrambleId) { return true; }
            currScramble.time      = timerStopData.rawTimeCs;
            currScramble.isDNF     = timerStopData.isDNF;
            currScramble.isPlusTwo = timerStopData.isPlusTwo;
         */

        // integers only, and update complete status and raw "time" attribute
        $(".single-time.fmc>.time-value").on("keypress keyup blur", function(e) {
            $(this).val($(this).text().replace(/[^\d].+/, ""));
            if (parseInt($(this).text()) > 0) {
                $(this).parent().addClass('complete');
                console.log($(this).parent());
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
    };

    /**
     * Wire up the left-click context menu on each solve card for adding and removing
     * solve penalties (DNF, +2), and retrying a solve.
     */
    TimerScreenManager.prototype._wire_solve_context_menu = function(compEventId) {
        // Clear all the penalties, set visible time back to the time of the solve
        var clearPenalty = function($solveClicked) {
            var scrambleId = $solveClicked.attr('data-id');
            app.eventsDataManager.clearPenalty(compEventId, scrambleId);

            var solveTime = app.eventsDataManager.getSolveRecord(compEventId, scrambleId).time;
            $solveClicked.find('.time-value').html(app.convertRawCsForSolveCard(solveTime));
        };

        // Set DNF penalty, set visible time to 'DNF'
        var setDNF = function($solveClicked) {
            var scrambleId = $solveClicked.attr('data-id');
            app.eventsDataManager.setDNF(compEventId, scrambleId);

            $solveClicked.find('.time-value').html("DNF");
        };

        // Set +2 penalty, set visible time to the
        // actual time + 2 seconds, and "+" mark to indicate penalty
        var setPlusTwo = function($solveClicked) {
            var scrambleId = $solveClicked.attr('data-id');
            app.eventsDataManager.setPlusTwo(compEventId, scrambleId);

            var solveTime = app.eventsDataManager.getSolveRecord(compEventId, scrambleId).time;
            $solveClicked.find('.time-value').html(app.convertRawCsForSolveCard(solveTime + 200) + "+");
        };

        // Check if the selected solve is complete
        var isComplete = function($solveClicked) {
            var scrambleId = $solveClicked.attr('data-id');
            return app.eventsDataManager.getSolveRecord(compEventId, scrambleId).status == 'complete';
        };

        // Check if the selected solve has DNF penalty
        var hasDNF = function($solveClicked) {
            var scrambleId = $solveClicked.attr('data-id');
            return app.eventsDataManager.getSolveRecord(compEventId, scrambleId).isDNF;
        };

        // Check if the selected solve has +2 penalty
        var hasPlusTwo = function($solveClicked) {
            var scrambleId = $solveClicked.attr('data-id');
            return app.eventsDataManager.getSolveRecord(compEventId, scrambleId).isPlusTwo;
        };

        // Retry the selected solve - set it as the only active solve, attach the timer, prepare the timer
        var retrySolve = function($solveClicked) {
            var scrambleId = $solveClicked.attr('data-id');

            // Remove active status from whichever solve is currently active, if any.
            // Set the selected solve as active.
            $('.single-time.active').removeClass('active');
            $solveClicked.addClass('active');

            // Reset the timer, and attach it to this solve card
            app.timer.reset();
            app.timer.attachToScramble(parseInt(scrambleId));
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