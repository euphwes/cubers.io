(function() {
    var app = window.app;

    var NON_FMC_SOLVE_CARD_SELECTOR = '.single-time:not(.fmc)';
    var FMC_CARD_SELECTOR           = '.single-time.fmc';
    var FMC_LENGTH_TEXT_SELECTOR    = '.time-value';
    var SOLVE_CARD_ACTIVE_SELECTOR  = '.single-time.active';

    /**
     * Manages the overall timer page, including events wired when the page is shown
     */
    function TimerScreenManager() {
        this.$timer_div = $('#timer_panel');
        this.timer_panel_template = Handlebars.compile($('#timer-template').html());

        this._registerAppModeManagerListeners();
    };

    /**
     * Destroys the context menu and hides the timer screen. The context menu needs to
     * be destroyed so that next time this page is show, the menu's functions reference
     * the new competition event ID.
     */
    TimerScreenManager.prototype._hideTimerScreen = function() {
        $.contextMenu('destroy', NON_FMC_SOLVE_CARD_SELECTOR);
        this.$timer_div.ultraHide();
    };

    /**
     * Shows the timer screen for the specified event.
     */
    TimerScreenManager.prototype._showTimerScreen = function($selected_event) {
        var events = app.eventsDataManager.getEventsData();
        var comp_event_id = $selected_event.attr('data-comp_event_id');

        var scramblePreviewUnsupportedEvents = ["2BLD", "3BLD", "4BLD", "5BLD", "COLL",
        "Kilominx", "3x3 Mirror Blocks/Bump", "3x3x4", "3x3x2", "3x3x5", "Void Cube",
        "2-3-4 Relay", "3x3 Relay of 3", "PLL Time Attack", "Redi Cube"];

        var scramblePreviewIsSupported = !scramblePreviewUnsupportedEvents.includes($selected_event.data('event_name'));

        var data = {
            comp_event_id              : comp_event_id,
            event_id                   : $selected_event.data('event_id'),
            event_name                 : $selected_event.data('event_name'),
            scrambles                  : events[comp_event_id]['scrambles'],
            total_solves               : events[comp_event_id]['scrambles'].length,
            comment                    : events[comp_event_id].comment,
            isMobile                   : app.is_mobile,
            scramblePreviewIsSupported : scramblePreviewIsSupported,
        };

        // FMC requires manual entry of integer times, and no timer
        data.isFMC = data.event_name === 'FMC';

        // Render the Handlebars template for the timer panel with the event-related data
        // collected above, and set it as the new html for the timer panel div
        this.$timer_div.html($(this.timer_panel_template(data)));
        this.$timer_div.ultraShow();

        // Make sure the user doesn't highlight the timer text when they use the timer
        $('.timer-wrapper').disableTextSelect();

        // Make sure the timer knows which competition event this is, so the handlers of the timer-stop
        // event know which solve to update
        app.timer.setCompEventId(comp_event_id);

        app.currentScramblesManager.attachFirstScramble(comp_event_id);

        // Wire up the stuff common to both FMC and non-FMC events
        app.appModeManager.wire_return_to_events_from_timer();
        this._wire_comment_box(comp_event_id);
        this._wire_scramble_preview_click();
        this._wire_mobile_scramble_preview_click();
        this._wire_resize_scramble_redraw();

        if (data.isFMC) {
            this._wire_fmc_card_solve_typing(comp_event_id);
            this._wire_fmc_card_click(comp_event_id);
        } else {
            this._wire_solve_context_menu(comp_event_id);
        }
    };

    TimerScreenManager.prototype._wire_resize_scramble_redraw = function() {
        $(window).on('resize', function(){
            app.scrambleImageGenerator.reset();
            app.scrambleImageGenerator.showNormalImage();
        });
    };

    /**
     * Wire up the scramble preview click to open larger preview.
     */
    TimerScreenManager.prototype._wire_scramble_preview_click = function() {
        $('.scramble_preview_buffer.clickable').click(function(){
            app.scrambleImageGenerator.showLargeImage();
            $('#fade-wrapper').fadeIn().addClass('shown');
            $('#fade-wrapper').click(function(){
                $(this).fadeOut(function(){
                    $(this).removeClass('shown');
                });
            })
        });
    };

    /**
     * Wire up the scramble preview button click on mobile.
     */
    TimerScreenManager.prototype._wire_mobile_scramble_preview_click = function() {
        $('#show-scramble-btn>.btn-return').click(function(){
            app.scrambleImageGenerator.showLargeImageForMobile();
            $('#fade-wrapper').fadeIn().addClass('shown');
            $('#fade-wrapper').click(function(){
                $(this).fadeOut(function(){
                    $(this).removeClass('shown');
                });
            })
        });
    };

    /**
     * Wire up the comment box to save the comment to the events data when done typing.
     */
    TimerScreenManager.prototype._wire_comment_box = function(comp_event_id) {
        var comment_timeout = null;
        var $comment = $('#comment_' + comp_event_id);
        $comment.keyup(function(){
            clearTimeout(comment_timeout);
            comment_timeout = setTimeout(function(){
                app.eventsDataManager.setCommentForEvent($comment.val(), comp_event_id);
            }, 500);
        });
    };

    /**
     * Wire up the keypress handler on the solve length entry for the FMC cards.
     * After debouncing, sends the solve length to the events data manager to be recorded,
     * and have the event data be properly updated.
     */
    TimerScreenManager.prototype._wire_fmc_card_solve_typing = function(comp_event_id) {
        var fmcTimeout = null;

        // Swallow tab key, prevent tabbing into next contenteditable div
        $(FMC_LENGTH_TEXT_SELECTOR).keydown(function (e) {
            var code = (e.keyCode ? e.keyCode : e.which);
            if (code == 9) { e.preventDefault(); return; }
        });

        // Determine the solve length entered in the box. If there's a value, set the
        // solve length for that FMC solve and mark complete, otherwise unset the value for this solve
        var updateFmcSolveRecord = function() {
            var solve_length = parseInt($(this).text());
            var scramble_id  = $(this).parent().attr('data-id');
            if (solve_length > 0) {
                $(this).parent().addClass('complete');
                app.eventsDataManager.setFMCSolveLength(comp_event_id, scramble_id, solve_length);
            } else {
                $(this).parent().removeClass('complete'); 
                app.eventsDataManager.unsetFMCSolve(comp_event_id, scramble_id);
            }
        };

        // Set up a keypress listener on the FMC cards
        $(FMC_LENGTH_TEXT_SELECTOR).on("keyup keypress blur", function(e) {
            clearTimeout(fmcTimeout);

            // Only allow digits
            $(this).val($(this).text().replace(/[^\d].+/, ""));
            if ((e.which < 48 || e.which > 57)) { e.preventDefault(); }

            // After waiting for the user to stop typing, update the solve record
            fmcTimeout = setTimeout(updateFmcSolveRecord.bind(this), 500);
        });
    };

    /**
     * Wire up the click handler for the FMC solve cards to set the correct card as active,
     * and to display the scramble
     */
    TimerScreenManager.prototype._wire_fmc_card_click = function(comp_event_id) {
        $(FMC_CARD_SELECTOR).click(function(){
            $(SOLVE_CARD_ACTIVE_SELECTOR).removeClass('active');
            $(this).addClass('active');
            app.currentScramblesManager.attachSpecifiedScramble(comp_event_id, $(this).attr('data-id'));
        });
    };

    /**
     * Wire up the left-click context menu on each solve card for adding and removing
     * solve penalties (DNF, +2), and retrying a solve.
     */
    TimerScreenManager.prototype._wire_solve_context_menu = function(compEventId) {
        // Clear all the penalties, set visible time back to the time of the solve
        var clearPenalty = function($solve_clicked) {
            var scramble_id = $solve_clicked.attr('data-id');
            app.eventsDataManager.clearPenalty(compEventId, scramble_id);

            var solve_time = app.eventsDataManager.getSolveRecord(compEventId, scramble_id).time;
            $solve_clicked.find(FMC_LENGTH_TEXT_SELECTOR).html(app.convertRawCsForSolveCard(solve_time));
        };

        // Set DNF penalty, set visible time to 'DNF'
        var setDNF = function($solve_clicked) {
            var scramble_id = $solve_clicked.attr('data-id');
            app.eventsDataManager.setDNF(compEventId, scramble_id);

            $solve_clicked.find(FMC_LENGTH_TEXT_SELECTOR).html("DNF");
        };

        // Set +2 penalty, set visible time to the
        // actual time + 2 seconds, and "+" mark to indicate penalty
        var setPlusTwo = function($solve_clicked) {
            var scramble_id = $solve_clicked.attr('data-id');
            app.eventsDataManager.setPlusTwo(compEventId, scramble_id);

            var solve_time = app.eventsDataManager.getSolveRecord(compEventId, scramble_id).time;
            $solve_clicked.find(FMC_LENGTH_TEXT_SELECTOR).html(app.convertRawCsForSolveCard(solve_time + 200) + "+");
        };

        // Check if the selected solve is complete
        var isComplete = function($solve_clicked) {
            var scramble_id = $solve_clicked.attr('data-id');
            return app.eventsDataManager.getSolveRecord(compEventId, scramble_id).status == 'complete';
        };

        // Check if the selected solve has DNF penalty
        var hasDNF = function($solve_clicked) {
            var scramble_id = $solve_clicked.attr('data-id');
            return app.eventsDataManager.getSolveRecord(compEventId, scramble_id).isDNF;
        };

        // Check if the selected solve has +2 penalty
        var hasPlusTwo = function($solve_clicked) {
            var scramble_id = $solve_clicked.attr('data-id');
            return app.eventsDataManager.getSolveRecord(compEventId, scramble_id).isPlusTwo;
        };

        // Delete the selected solve - remove the recorded time from it.
        var deleteSolve = function($solve_clicked) {
            var scramble_id = $solve_clicked.attr('data-id');
            app.eventsDataManager.deleteSolveTime(compEventId, scramble_id);
        };

        // Allow manual entry
        var manualEntry = function($solve_clicked) {
            var scramble_id = $solve_clicked.attr('data-id');
            bootbox.prompt({
                title: "Enter your time",
                buttons: {
                    confirm: {
                        label: 'Ok',
                        className: 'btn-success'
                    },
                },
                callback: function(result) {
                    if (!result) { return; }
                    var cs = app.hmsToCentiseconds(result);
                    if (isNaN(cs)) {
                        bootbox.alert("Please enter a valid time.");
                        return;
                    }
                    app.eventsDataManager.setSolveTimeForManualEntry(compEventId, scramble_id, cs);
                }
            });
        };

        $.contextMenu({
            selector: NON_FMC_SOLVE_CARD_SELECTOR,
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
                "manual" : {
                    name: "Manual time entry",
                    icon: "fas fa-edit",
                    callback: function(itemKey, opt, e) { manualEntry($(opt.$trigger)); }
                },
                "sep2": "---------",
                "delete": {
                    name: "Delete time",
                    icon: "fas fa-trash",
                    callback: function(itemKey, opt, e) { deleteSolve($(opt.$trigger)); },
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