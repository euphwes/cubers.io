(function() {

    var EVENT_TIMER_START    = 'event_timer_start';
    var EVENT_TIMER_INTERVAL = 'event_timer_interval';
    var EVENT_TIMER_STOP     = 'event_timer_stop';
    var EVENT_TIMER_ATTACHED = 'event_timer_attached';
    var EVENT_TIMER_RESET    = 'event_timer_reset';
    var EVENT_TIMER_ARMED    = 'event_timer_armed';

    function Timer() {
        window.app.EventEmitter.call(this);  // Timer is an EventEmitter

        //this.$seconds = $('#seconds');
        //this.$centiseconds = $('#centiseconds');
        //this.$dot = $('#dot');
        //this.$singleSolveTimeElem = null;

        this.startTime = 0;
        this.elapsedTime = 0;
        this.timerInterval = null;
        this.scrambleId = 0;

        // wire event handlers to listen which screens are being shown
        // disable timer when screens other than timer panel are shown
        // enable timer when timer panel is shown

        this._enable();
    };
    Timer.prototype = Object.create(window.app.EventEmitter.prototype);

    /**
     * Enables the timer by setting up keyboard event listeners for starting
     * or stopping the timer
     */
    Timer.prototype._enable = function() {
        // If the spacebar is already down when entering here, that probably means
        // that the user held it after completing the previous solve. Wait for the
        // user to release the spacebar by setting a short timeout to revisit this function
        if (kd.SPACE.isDown()) {
            setTimeout(this._enable.bind(this), 200);
            return;
        }

        // Pressing the spacebar down "arms" the timer to prepare it to start when
        // the user releases the spacebar. Don't arm the timer if the comment input
        // box has focus.
        var armed = false;
        kd.SPACE.down(function() {
            // TODO: don't arm if the comment box has focus, probably
            // can just check this by class rather than ID
            //if ($('#comment_' + this.timer.comp_event_id).is(":focus")) { return; }
            armed = true;
            this.emit(EVENT_TIMER_ARMED);
        }.bind(this));

        // When the spacebar is released, unbind the spacebar keydown and keyup events
        // and bind a new keydown event which will stop the timer
        kd.SPACE.up(function() {
        
            // do nothing if the timer isn't armed yet by a spacebar keydown
            if (!armed) { return; }
            
            // unbind the current events
            kd.SPACE.unbindUp(); kd.SPACE.unbindDown();
            
            // start the timer, and bind a new event to spacebar keydown 
            // to stop the timer and then automatically advance to the next scramble
            this._start();
            $(document).keydown(function(e) {
                //var code = (e.keyCode ? e.keyCode : e.which);
                //if (code == 27) {
                //    //TODO: 27 == esc, cancel the timer and don't record time
                //    e.preventDefault();
                //    return;
                //}
                this._stop();

                // TODO: this belongs somewhere else, in a scramble display manager?
                //this.auto_advance_timer_scramble();
            }.bind(this));
        }.bind(this));
    };

    /**
     * "Attach" the timer to a specific scrambleId so it can send
     * appropriate data when it emits events.
     */
    Timer.prototype.attachToScramble = function(scrambleId) {
        this.scrambleId = scrambleId;
        this.emit(EVENT_TIMER_ATTACHED, scrambleId);

        // ---------------------------------------------------------------
        // this stuff below belongs to something else

        //this.$singleSolveTimeElem = solveTimeElem;
        //this.$singleSolveTimeElem.addClass('active');
        //var newScramble = this.$singleSolveTimeElem.data('scramble');

        //var renderedScramble = "";
        //$.each(newScramble.split('\n'), function(i, piece){
        //    renderedScramble += "<p>" + piece + "</p>";
        //});

        //var $scrambleHolder = $('.scramble-wrapper>div');
        //$scrambleHolder.html(renderedScramble);
    };
 
    /**
     * Starts the timer. Captures the start time so we can determine elapsed time on
     * subsequent ticks.
     */
    Timer.prototype._start = function() {
        this.startTime = new Date();
        this.timerInterval = setInterval(this._timerIntervalFunction.bind(this), 42);
        this.emit(EVENT_TIMER_START);

        // ---------------------------------------------------------------
        // this stuff below belongs to something else

        //this.$dot.html('.');
    };

    /**
     * Stops the timer, determines the elapsed time, and updates the attached solve element
     * with a user-friendly representation of the elapsed time. Also marks the solve complete,
     * and sets the data attribute for raw time in centiseconds.
     */
    Timer.prototype._stop = function() {
    
        // stop the recurring tick function which continuously updates the timer, and unbind
        // the keyboard space keypress events which handle the timer start/top
        clearInterval(this.timerInterval);
        kd.SPACE.unbindDown(); kd.SPACE.unbindUp();
        $(document).unbind("keydown");

        // calculate elapsed time, separate seconds and centiseconds, and get the
        // "full time" string as seconds converted to minutes + decimal + centiseconds
        this.elapsedTime = (new Date()) - this.startTime;

        var s = this.elapsedTime.getSecondsFromMs();
        var cs = this.elapsedTime.getTwoDigitCentisecondsFromMs();
        var friendlySeconds = window.app.convertSecondsToMinutes(s);

        var eventData = {};
        eventData.elapsedTime          = this.elapsedTime;
        eventData.scrambleId           = this.scrambleId;
        eventData.friendlySeconds      = friendlySeconds;
        eventData.friendlyCentiseconds = cs;
        eventData.friendlyTimeFull     = friendlySeconds + "." + cs;
        eventData.rawTimeCs            = parseInt(s*100) + parseInt(cs);

        this.emit(EVENT_TIMER_STOP, eventData);
        this._reset();
        setTimeout(this._enable.bind(this), 1000);

        // ---------------------------------------------------------------
        // this stuff below belongs to something else

        // ensure the timer display shows the same time as the solve card
        //this.$seconds.html(window.app.convertSecondsToMinutes(s));
        //this.$centiseconds.html(cs);
    };

    /**
     * Resets the timer, clearing start and elapsed time, and sets the visible timer elements
     * to the zero state.
     */
    Timer.prototype._reset = function() {
        this.startTime = 0;
        this.elapsedTime = 0;

        this.emit(EVENT_TIMER_RESET);

        // ---------------------------------------------------------------
        // this stuff below belongs to something else

        //this.$seconds.html('0');
        //this.$dot.html('.');
        //this.$centiseconds.html('00');
    };

    /**
     * Checks the current time against the start time to determine
     * elapsed time, and updates the visible timer accordingly.
     */
    Timer.prototype._timerIntervalFunction = function() {
        var now = new Date();
        var diff = now - this.startTime;
        var s = diff.getSecondsFromMs();
        var cs = diff.getTwoDigitCentisecondsFromMs();

        var eventData = {};
        eventData.friendlySeconds = window.app.convertSecondsToMinutes(s);
        eventData.friendlyCentiseconds = cs;

        this.emit(EVENT_TIMER_INTERVAL, eventData);

        // ---------------------------------------------------------------
        // this stuff below belongs to something else

        //this.$seconds.html(window.app.convertSecondsToMinutes(s));
        //this.$centiseconds.html(cs);
    };

    // Make timer and event names visible at app scope
    window.app.Timer = Timer;
    window.app.EVENT_TIMER_STOP     = EVENT_TIMER_STOP;
    window.app.EVENT_TIMER_START    = EVENT_TIMER_START;
    window.app.EVENT_TIMER_INTERVAL = EVENT_TIMER_INTERVAL;
    window.app.EVENT_TIMER_ATTACHED = EVENT_TIMER_ATTACHED;
    window.app.EVENT_TIMER_RESET    = EVENT_TIMER_RESET;
    window.app.EVENT_TIMER_ARMED    = EVENT_TIMER_ARMED;
})();