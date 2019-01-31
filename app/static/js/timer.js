(function() {
    var app = window.app;

    // These are the events that the timer can emit
    var EVENT_TIMER_START          = 'event_timer_start';
    var EVENT_TIMER_INTERVAL       = 'event_timer_interval';
    var EVENT_INSPECTION_INTERVAL  = 'event_inspection_interval';
    var EVENT_INSPECTION_STARTED   = 'event_inspection_started';
    var EVENT_INSPECTION_ARMED     = 'event_inspection_armed';
    var EVENT_TIMER_STOP           = 'event_timer_stop';
    var EVENT_TIMER_ARMED          = 'event_timer_armed';
    var EVENT_TIMER_CANCELLED      = 'event_timer_cancelled';

    // These are the states the the timer can be in
    var STATE_INACTIVE         = 0;
    var STATE_ARMED            = 1;
    var STATE_INSPECTION       = 2;
    var STATE_INSPECTION_ARMED = 3;
    var STATE_RUNNING          = 4;
    var STATE_DONE             = 5;

    // Dev flag for debugging timer state
    var debug_timer_state = false;
    var timer_state_map = {
        0: 'inactive',
        1: 'armed',
        2: 'inspection',
        3: 'inspection armed',
        4: 'running',
        5: 'done',
    };

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
        this.inspection_start_time = 0;
        this.inspection_end_time = 0;
        this.auto_dnf = false;
        this.auto_plus_two = false;

        this.isTouchDown = false;

        // values related to inspection time starting point and automatic penalty thresholds
        this.INSP_TIME_START = 15;
        this.AUTO_DNF_THRESHOLD = -2;
        this.AUTO_PLUS_TWO_THRESHOLD = 0;
        this.apply_auto_dnf = false;
        this.apply_auto_plus_two = false;

        // keydrown.js's keyboard state manager is tick-based
        // this is boilerplate to make sure the kd namespace has a recurring tick
        kd.run(function () { kd.tick(); });

        this._registerAppModeManagerListeners();
    }
    Timer.prototype = Object.create(app.EventEmitter.prototype);

    /**
     * Sets the timer's competition event ID.
     */
    Timer.prototype.setCompEventId = function(comp_event_id) {
        this.comp_event_id = comp_event_id;
    };

    /**
     * If the event is a blind event, there is no inspection time. Otherwise check the setting
     * to determine whether or not to use inspection time.
     */
    Timer.prototype.determineIfUsingInspectionBasedOnEvent = function(event_name) {
        if (["2BLD", "3BLD", "4BLD", "5BLD"].includes(event_name)) {
            this.useInspectionTime = false;
        } else {
            this.useInspectionTime = app.userSettingsManager.get_setting(app.Settings.USE_INSPECTION_TIME);
        }
    };

    /**
     * "Attach" the timer to a specific scramble_id so it can send
     * appropriate data when it emits events.
     */
    Timer.prototype.attachToScramble = function(scramble_id) {
        this.scramble_id = scramble_id;
        this._enable();
    };

    /**
     * Sets the timer state and optionally logs the new state to the console.
     */
    Timer.prototype._setState = function(new_state) {
        this.state = new_state;
        if (app.debug_timer_state) {
            console.log(timer_state_map[new_state]);
        }
    };

    /**
     * Enables the timer by binding keyboard and touch event listeners
     */
    Timer.prototype._enable = function() {
        // If the spacebar or touch is already down when entering here, that probably means
        // that the user held it after completing the previous solve. Wait for the
        // user to release the spacebar/touch by setting a short timeout to revisit this function
        if (kd.SPACE.isDown() || this.isTouchDown) {
            setTimeout(this._enable.bind(this), 200);
            return;
        }

        // wire the keyboard events
        $(document).keydown(this._handleOtherKeyDown.bind(this));
        kd.SPACE.up(this._handleSpaceUp.bind(this));
        kd.SPACE.down(this._handleSpaceDown.bind(this));

        // wire the touch events, basically treating touchend as spacebar up and touchstart
        // as spacebar down
        if (app.is_mobile) {
            $('.timer-wrapper').on("touchend", function(e){
                this.isTouchDown = false;
                this._handleSpaceUp.bind(this)(e);
            }.bind(this));
            $('.timer-wrapper').on("touchstart", function(e){
                this.isTouchDown = true;
                this._handleSpaceDown.bind(this)(e);
            }.bind(this));
        }

        this._setState(STATE_INACTIVE);
    };

    /**
     * Disables the timer by disabling the keypress and touch events, and disables the interval
     * function which ticks by elapsed time.
     */
    Timer.prototype._disable = function() {
        // no more ticking
        clearInterval(this.timer_interval);
        clearInterval(this.inspection_interval);

        // unbind the keyboard events
        $(document).off('keydown');
        kd.SPACE.unbindUp();
        kd.SPACE.unbindDown();

        // unbind the touch events
        $('.timer-wrapper').off("touchstart");

        // do not unbind the touchend because then we can't keep track of whether
        // the touch event has ended
        // $('.timer-wrapper').off("touchend");
    };

    /**
     * Handles the space down event, moving the timer to the appropriate state based on its
     * current state and starting whatever logic needs to be started.
     */
    Timer.prototype._handleSpaceDown = function(e) {
        // If the timer is inactive, arm the timer so it's ready to start.
        if (this.state == STATE_INACTIVE) {
            // If the comment box has focus, don't start the timer
            if ($(".comment-upload textarea").is(":focus")) { return; }
            this._arm();
            e.preventDefault();
            return;
        }

        // If inspection is in progress, set "inspection armed" so releasing will start the timer
        if (this.state == STATE_INSPECTION) {
            this._armInspection();
            e.preventDefault();
            return;
        }

        // If the timer is running, stop it
        if (this.state == STATE_RUNNING) {
            this._stop();
            e.preventDefault();
            return;
        }

        e.preventDefault();
    };

    /**
     * Handles the space key up event, moving the timer to the appropriate state based on its
     * current state and starting whatever logic needs to be started.
     */
    Timer.prototype._handleSpaceUp = function(e) {
        // If the timer is stopped and the space goes up or touch release, don't do anything
        if (this.state == STATE_DONE) {
            e.preventDefault();
            return;
        }

        // If the timer is armed...
        if (this.state == STATE_ARMED) {
            if (this.useInspectionTime) {
                // ... start inspection
                this._startInspection();
            } else {
                // ... start the timer
                this._start();
            }
            e.preventDefault();
            return;
        }

        // The the timer's inspection has been armed, then start the timer
        if (this.state == STATE_INSPECTION_ARMED) {
            this._start();
            e.preventDefault();
            return;
        }

        e.preventDefault();
    };

    /**
     * Handles the keydown event for keys other than space
     */
    Timer.prototype._handleOtherKeyDown = function(e) {
        // If the timer isn't running, don't do anything
        if (this.state != STATE_RUNNING) {
            return;
        }

        // Get the event's key code
        var code = (e.keyCode ? e.keyCode : e.which);

        // Key code 32 is the spacebar, which is being handled by the keydrown.js handler elsewhere.
        // Just bail, don't handle it here.
        if (code == 32) { return; }

        // Key code 27 is ESC, which should cancel the timer. Everything else should just stop it
        var shouldCancelTimer = (code == 27);
        this._stop(shouldCancelTimer);
        e.preventDefault();
    };

    /**
     * Arms the timer by putting it a state indicating it's ready to start running.
     */
    Timer.prototype._arm = function() {
        this._setState(STATE_ARMED);
        this.emit(EVENT_TIMER_ARMED);
    }

    /**
     * Arms the timer from within inspection by putting it a state indicating it's ready to start running.
     */
    Timer.prototype._armInspection = function () {
        this._setState(STATE_INSPECTION_ARMED);
        this.emit(EVENT_INSPECTION_ARMED);
    }

    /**
     * Starts the timer. Captures the start time so we can determine elapsed time on subsequent ticks.
     */
    Timer.prototype._start = function() {

        // If inspection was previously running, stop the inspection
        if (this.inspection_interval) {
            clearInterval(this.inspection_interval);
        }

        this._setState(STATE_RUNNING);
        this.start_time = new Date();
        this.timer_interval = setInterval(this._timer_intervalFunction.bind(this), 42);
        this.emit(EVENT_TIMER_START);
    };

    /**
     * Starts the inspection countdown.
     */
    Timer.prototype._startInspection = function() {
        this.emit(EVENT_INSPECTION_STARTED, this.INSP_TIME_START);
        this._setState(STATE_INSPECTION);
        this.inspection_start_time = new Date();
        this.inspection_interval = setInterval(this._inspection_intervalFunction.bind(this), 42);
    };

    /**
     * Stops the timer, determines the elapsed time, and updates the attached solve element
     * with a user-friendly representation of the elapsed time. Also marks the solve complete,
     * and sets the data attribute for raw time in centiseconds.
     */
    Timer.prototype._stop = function(timerCancelled) {

        timerCancelled = timerCancelled || false; // default value of false

        this._setState(STATE_DONE);
        this._disable();

        // If the timer was cancelled, don't record the time. Emit an event so the visible timer
        // gets updated back to zeros. Re-enable the timer.
        if (timerCancelled) {
            // reset the flags to auto-apply penalties if inspection is too long
            // reset stuff related to inspection time, to start the next solve on a clean slate
            this.inspection_start_time = 0;
            this.inspection_end_time = 0;
            this.apply_auto_dnf = false;
            this.apply_auto_plus_two = false;

            this.emit(EVENT_TIMER_CANCELLED);
            this._enable();
            return;
        }

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

        // check auto-penalty flags if we did inspection, else set those flags to false
        if (this.useInspectionTime) {
            data.isDNF = this.apply_auto_dnf;
            data.isPlusTwo = this.apply_auto_plus_two;
        } else {
            data.isDNF = false;
            data.isPlusTwo = false;
        }

        // emit the event which notifies everybody else that the timer has stopped
        this.emit(EVENT_TIMER_STOP, data);

        // reset the flags to auto-apply penalties if inspection is too long
        // reset stuff related to inspection time, to start the next solve on a clean slate
        this.inspection_start_time = 0;
        this.inspection_end_time = 0;
        this.apply_auto_dnf = false;
        this.apply_auto_plus_two = false;
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
     * Checks the current time against the start time to determine elapsed time.
     */
    Timer.prototype._inspection_intervalFunction = function() {
        var inspection_elapsed_seconds = ((new Date()) - this.inspection_start_time).getSecondsFromMs();
        var seconds_remaining = this.INSP_TIME_START - inspection_elapsed_seconds;

        if (seconds_remaining < this.AUTO_DNF_THRESHOLD) {
            this.apply_auto_dnf = true;
            this.apply_auto_plus_two = false;
            console.log('auto dnf');
            this._stop();
            return;
        } else if (seconds_remaining < this.AUTO_PLUS_TWO_THRESHOLD) {
            console.log('auto plus 2');
            this.apply_auto_plus_two = true;
        }

        this.emit(EVENT_INSPECTION_INTERVAL, {seconds_remaining});
    };

    /**
     * Register handlers for AppModeManager events.
     */
    Timer.prototype._registerAppModeManagerListeners = function() {
        app.appModeManager.on(app.EVENT_APP_MODE_TO_MAIN, this._disable.bind(this));
        app.appModeManager.on(app.EVENT_APP_MODE_TO_SUMMARY, this._disable.bind(this));
    };

    // Make timer and event names visible at app scope
    app.Timer = Timer;
    app.EVENT_TIMER_STOP           = EVENT_TIMER_STOP;
    app.EVENT_TIMER_START          = EVENT_TIMER_START;
    app.EVENT_TIMER_INTERVAL       = EVENT_TIMER_INTERVAL;
    app.EVENT_INSPECTION_INTERVAL  = EVENT_INSPECTION_INTERVAL;
    app.EVENT_INSPECTION_STARTED   = EVENT_INSPECTION_STARTED;
    app.EVENT_INSPECTION_ARMED     = EVENT_INSPECTION_ARMED;
    app.EVENT_TIMER_ARMED          = EVENT_TIMER_ARMED;
    app.EVENT_TIMER_CANCELLED      = EVENT_TIMER_CANCELLED;

    app.debug_timer_state = debug_timer_state;
})();