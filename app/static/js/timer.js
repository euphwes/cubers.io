(function() {
    var app = window.app;

    // These are the events that Timer can emit
    var EVENT_TIMER_START    = 'event_timer_start';
    var EVENT_TIMER_INTERVAL = 'event_timer_interval';
    var EVENT_TIMER_STOP     = 'event_timer_stop';
    var EVENT_TIMER_RESET    = 'event_timer_reset';
    var EVENT_TIMER_ARMED    = 'event_timer_armed';

    /**
     * The solve timer which tracks elapsed time.
     */
    function Timer() {
        app.EventEmitter.call(this);

        this.start_time = 0;
        this.elapsed_time = 0;
        this.timer_interval = null;
        this.scramble_id = 0;
        this.comp_event_id = 0;

        // keydrown.js's keyboard state manager is tick-based
        // this is boilerplate to make sure the kd namespace has a recurring tick
        kd.run(function () { kd.tick(); });
    };
    Timer.prototype = Object.create(app.EventEmitter.prototype);

    /**
     * Sets the timer's competition event ID.
     */
    Timer.prototype.setCompEventId = function(comp_event_id) {
        this.comp_event_id = comp_event_id;
    }

    /**
     * Enables the timer by setting up keyboard event listeners for starting
     * or stopping the timer
     */
    Timer.prototype._enable = function() {

        if (app.is_mobile) {
            $('.timer-wrapper').off("touchend");
            $('.timer-wrapper').on("touchend", function() {
                // start the timer, and bind a new event to spacebar keydown 
                // to stop the timer and then automatically advance to the next scramble
                $('.timer-wrapper').off("touchend");
                this._start();
                $('.timer-wrapper').on("touchend", function() {
                    $('.timer-wrapper').off("touchend");
                    this._stop();
                }.bind(this));
            }.bind(this));
            return;
        }

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
            if ($('#comment_' + this.comp_event_id).is(":focus")) { return; }
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
            }.bind(this));
        }.bind(this));
    };

    /**
     * "Attach" the timer to a specific scramble_id so it can send
     * appropriate data when it emits events.
     */
    Timer.prototype.attachToScramble = function(scramble_id) {
        this.scramble_id = scramble_id;
        setTimeout(this._enable.bind(this), 500);
    };
 
    /**
     * Starts the timer. Captures the start time so we can determine elapsed time on subsequent ticks.
     */
    Timer.prototype._start = function() {
        this.start_time = new Date();
        this.timer_interval = setInterval(this._timer_intervalFunction.bind(this), 42);
        this.emit(EVENT_TIMER_START);
    };

    /**
     * Stops the timer, determines the elapsed time, and updates the attached solve element
     * with a user-friendly representation of the elapsed time. Also marks the solve complete,
     * and sets the data attribute for raw time in centiseconds.
     */
    Timer.prototype._stop = function() {
        this._disable();

        // calculate elapsed time, 
        this.elapsed_time = (new Date()) - this.start_time;

        // separate seconds and centiseconds, and get the "full time" string
        // as seconds converted to minutes + decimal + centiseconds
        var s = this.elapsed_time.getSecondsFromMs();
        var cs = this.elapsed_time.getTwoDigitCentisecondsFromMs();
        var friendly_seconds = app.convertSecondsToMinutes(s);
        var full_time = friendly_seconds + "." + cs;

        var data = {};
        data.elapsed_time          = this.elapsed_time;
        data.scramble_id           = this.scramble_id;
        data.comp_event_id         = this.comp_event_id;
        data.friendly_seconds      = friendly_seconds;
        data.friendly_centiseconds = cs;
        data.friendly_time_full    = full_time;
        data.rawTimeCs             = parseInt(s*100) + parseInt(cs);
        data.isDNF                 = false;
        data.isPlusTwo             = false;

        // emit the event which notifies everybody else that the timer has stopped
        this.emit(EVENT_TIMER_STOP, data);
    };

    /**
     * Resets the timer.
     */
    Timer.prototype.reset = function() {
        this.start_time = 0;
        this.elapsed_time = 0;
        this.emit(EVENT_TIMER_RESET);
    };

    /**
     * Disables the timer by disabling the keypress events, and disables the interval function
     * which ticks by elapsed time.
     */
    Timer.prototype._disable = function() {
        clearInterval(this.timer_interval);
        kd.SPACE.unbindDown(); kd.SPACE.unbindUp();
        $(document).unbind("keydown");
        $('.timer-wrapper').off("mouseup");
    };

    /**
     * Checks the current time against the start time to determine elapsed time.
     */
    Timer.prototype._timer_intervalFunction = function() {
        var now = new Date();
        var diff = now - this.start_time;
        var s = diff.getSecondsFromMs();
        var cs = diff.getTwoDigitCentisecondsFromMs();

        var eventData = {};
        eventData.friendly_seconds = app.convertSecondsToMinutes(s);
        eventData.friendly_centiseconds = cs;

        this.emit(EVENT_TIMER_INTERVAL, eventData);
    };

    /**
     * Register handlers for AppModeManager events.
     */
    Timer.prototype._registerAppModeManagerListeners = function() {
        app.appModeManager.on(app.EVENT_APP_MODE_TO_MAIN, this._disable.bind(this));
        app.appModeManager.on(app.EVENT_APP_MODE_TO_SUMMARY, this._disable.bind(this));
        app.appModeManager.on(app.EVENT_APP_MODE_TO_TIMER, this._enable.bind(this));
    };

    // Make timer and event names visible at app scope
    app.Timer = Timer;
    app.EVENT_TIMER_STOP     = EVENT_TIMER_STOP;
    app.EVENT_TIMER_START    = EVENT_TIMER_START;
    app.EVENT_TIMER_INTERVAL = EVENT_TIMER_INTERVAL;
    app.EVENT_TIMER_RESET    = EVENT_TIMER_RESET;
    app.EVENT_TIMER_ARMED    = EVENT_TIMER_ARMED;
})();