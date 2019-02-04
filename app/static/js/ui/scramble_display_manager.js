(function() {
    var app = window.app;

    /**
     * Manages the scramble display
     */
    function ScrambleDisplayManager() {
        this._registerCurrentScramblesManagerHandlers();
        this._registerEventsDataManagerHandlers();
        this._wireResizeHandler();
    }

    /**
     * Wire up a listener for window resizes that refits the scramble text to the container for the new
     * window size.
     */
    ScrambleDisplayManager.prototype._wireResizeHandler = function() {
        $(window).on('resize', function(){
            textFit($('.scramble-wrapper .scram'), {multiLine: true, maxFontSize: 50});
        });
    };

    /**
     * Event handler for when a scramble is attached to the timer. Show the scramble in the display.
     */
    ScrambleDisplayManager.prototype._showScramble = function(eventData) {
        $('.scramble-wrapper .scram').removeClass('text-left').removeClass('code');
        var renderedScrambleText = eventData.scramble.scramble.split('\n').join('<br/>')
        if (eventData.eventName == 'Megaminx') {
            $('.scramble-wrapper .scram').addClass('text-left').addClass('code');
            console.log(renderedScrambleText);
            renderedScrambleText = this.__cleanupMegaminxScramble(renderedScrambleText);
            console.log(renderedScrambleText);
        }
        $('.scramble-wrapper .scram').html(renderedScrambleText);
        textFit($('.scramble-wrapper .scram'), {multiLine: true, maxFontSize: 50});
    };

    /**
     * Event handler for when there are no incomplete solves/scrambles left to attach.
     */
    ScrambleDisplayManager.prototype._showDone = function(comp_event_id) {

        comp_event_id = parseInt(comp_event_id);

        // If the event isn't complete, leave early and don't show the done message
        var data = app.eventsDataManager.getDataForEvent(comp_event_id);
        if (data.status != 'complete') { return; }

        // If the event is a blind event, don't show the "done" message unless all 3 solves are done.
        // Despite the fact we consider the event complete if any solves are complete, we don't want
        // to hide the next scramble if there are more left.
        if (data.event_format == 'Bo3') {
            if (data.blind_status != 'complete') { return; }
        }

        // If the event result still is empty, we haven't gotten the result back from the server.
        // Return early, and when the saveEvent call finishes, this will be called again
        if (!Boolean(data.result)) { return; }

        var start = (data.wasPbSingle || data.wasPbAverage) ? "Wow!" : "Congrats!";

        var text = start + "<br/>You've finished " + data.name + " with ";

        if (data.wasPbSingle && data.wasPbAverage) {
            text += "a PB single of " + data.single + " and a PB average of " + data.average + "!";
        } else if (data.wasPbAverage) {
            text += "a PB average of " + data.average + "!";
        } else if (data.wasPbSingle) {
            text += "a PB single of " + data.single + "!";
        } else {
            var eventFormatResultTypeMap = {
                'Bo3': 'a best single of ',
                'Bo1': 'a result of ',
                'Ao5': 'an average of ',
                'Mo3': 'a mean of ',
            };
            text += eventFormatResultTypeMap[data.event_format] + data.result + ".";
        }

        $('.scramble-wrapper .scram').html(text);
        textFit($('.scramble-wrapper .scram'));
    };

    ScrambleDisplayManager.prototype.__cleanupMegaminxScramble = function(scramble) {

        // Build up a list of indices of spaces following a U move
        var indicies_following_u = [];
        var i = -1;
        while ((i = scramble.indexOf("U ", i + 1)) >= 0) {
            indicies_following_u.push(i + 1); // +1 because indexOf will find the U, but we want 1 char later
        }

        // Build up a list of indices of spaces following a U' move
        var indicies_following_uprime = [];
        i = -1;
        while ((i = scramble.indexOf("U' ", i + 1)) >= 0) {
            indicies_following_uprime.push(i + 2); // +2 because indexOf will find the U', but we want 2 chars later
        }

        // Concatenate and sort the indicies of whitespace following a U or U'
        var indicies_after_u_moves = indicies_following_u.concat(indicies_following_uprime);
        indicies_after_u_moves.sort(function(a, b){return a-b});

        // We want insert a <br/> after every **other** U or U', starting on the 2nd one
        // After the others, we either want to insert a <br/> on mobile, or 2x or 3x non-breaking spaces,
        // depending on whether it's a U or U' we're following.
        //
        // The final effect is that we'll have 2 "chunks" of megaminx scramble on each line,
        // and the non-breaking spaces in combination with the monospace font we apply for megaminx scrambles
        // means everything will line up nicely. On mobile, we'll have 1 scramble chunk per line
        var break_here = false;
        var chars_added = 0;
        $.each(indicies_after_u_moves, function(_, ix) {
            if (break_here) {
                // adjust the index we're inserting into based on how many extra characters we've added
                ix += chars_added;
                scramble = scramble.slice(0, ix) + '<br/>' + scramble.slice(ix);
                chars_added += 5;
            } else {
                if (app.is_mobile) {
                    ix += chars_added;
                    scramble = scramble.slice(0, ix) + '<br/>' + scramble.slice(ix);
                    chars_added += 5;
                } else {
                    var is_follow_u = indicies_following_u.includes(ix);

                    // adjust the index we're inserting into based on how many extra characters we've added
                    ix += chars_added;
                    if (is_follow_u) {
                        scramble = scramble.slice(0, ix) + '&nbsp;&nbsp;&nbsp;' + scramble.slice(ix);
                        chars_added += 18;
                    } else {
                        scramble = scramble.slice(0, ix) + '&nbsp;&nbsp;' + scramble.slice(ix);
                        chars_added += 12;
                    }

                }
            }
            break_here = !break_here;
        });

        return scramble;
    };

    /**
     * Register handlers for current scrambles manager events.
     */
    ScrambleDisplayManager.prototype._registerCurrentScramblesManagerHandlers = function() {
        app.currentScramblesManager.on(app.EVENT_NOTHING_TO_ATTACH, this._showDone.bind(this));
        app.currentScramblesManager.on(app.EVENT_NEW_SCRAMBLE_ATTACHED, this._showScramble.bind(this));
    };

    /**
     * Register handlers for events data manager events.
     */
    ScrambleDisplayManager.prototype._registerEventsDataManagerHandlers = function() {
        app.eventsDataManager.on(app.EVENT_SUMMARY_CHANGE, this._showDone.bind(this));
    };

    // Make ScrambleDisplayManager visible at app scope
    app.ScrambleDisplayManager = ScrambleDisplayManager;
})();