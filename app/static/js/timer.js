(function() {
    var app = window.app;

    // NOTE: to whoever is looking at this file - it's freaking ugly
    // Will be reworking this in the near future to move to a state-based timer,
    // and away from this callback-ridden monstrosity.

    // These are the events that the timer can emit
    var EVENT_TIMER_START    = 'event_timer_start';
    var EVENT_TIMER_INTERVAL = 'event_timer_interval';
    var EVENT_TIMER_STOP     = 'event_timer_stop';
    var EVENT_TIMER_ARMED    = 'event_timer_armed';

    // These are the states the the timer can be in
    var STATE_INACTIVE   = 0;
    var STATE_ARMED      = 1;
    var STATE_INSPECTION = 2;  // not using this yet, but putting it in for a placeholder
    var STATE_RUNNING    = 3;
    var STATE_DONE       = 4;

    // Dev flag for debugging timer state
    var debug_timer_state = false;
    var timer_state_map = {
        0: 'inactive',
        1: 'armed',
        2: 'inspection',
        3: 'running',
        4: 'done',
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
     * "Attach" the timer to a specific scramble_id so it can send
     * appropriate data when it emits events.
     */
    Timer.prototype.attachToScramble = function(scramble_id) {
        this.scramble_id = scramble_id;
        setTimeout(this._enable.bind(this), 500);
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
        // If the spacebar is already down when entering here, that probably means
        // that the user held it after completing the previous solve. Wait for the
        // user to release the spacebar by setting a short timeout to revisit this function
        if (kd.SPACE.isDown()) {
            setTimeout(this._enable.bind(this), 200);
            return;
        }

        // wire the spacebar events
        kd.SPACE.up(this._handleSpaceUp.bind(this));
        kd.SPACE.down(this._handleSpaceDown.bind(this));

        // wire the touch events, basically treating touchend as spacebar up and touchstart
        // as spacebar down
        if (app.is_mobile) {
            $('.timer-wrapper').on("touchend", this._handleSpaceUp.bind(this));
            $('.timer-wrapper').on("touchstart", this._handleSpaceDown.bind(this));
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

        // unbind the spacebar events
        kd.SPACE.unbindUp();
        kd.SPACE.unbindDown();

        // unbind the touch events
        $('.timer-wrapper').off("touchend");
        $('.timer-wrapper').off("touchstart");
    };

    /**
     * Handles the space down event, moving the timer to the appropriate state based on its
     * current state and starting whatever logic needs to be started.
     */
    Timer.prototype._handleSpaceDown = function() {
        // If the timer is inactive, arm the timer so it's ready to start.
        if (this.state == STATE_INACTIVE) {
            this._arm();
            return;
        }
        // If the timer is running, stop it
        if (this.state == STATE_RUNNING) {
            this._stop();
            return;
        }
    };

    /**
     * Handles the space key up event, moving the timer to the appropriate state based on its
     * current state and starting whatever logic needs to be started.
     */
    Timer.prototype._handleSpaceUp = function() {
        // If the timer is armed, start the timer
        if (this.state == STATE_ARMED) {
            this._start();
            return;
        }
    };

    /**
     * Arms the timer by putting it a state indicating it's ready to start running.
     */
    Timer.prototype._arm = function() {
        this._setState(STATE_ARMED);
    }

    /**
     * Starts the timer. Captures the start time so we can determine elapsed time on subsequent ticks.
     */
    Timer.prototype._start = function() {
        this._setState(STATE_RUNNING);
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
        this._setState(STATE_DONE);
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
        app.appModeManager.on(app.EVENT_APP_MODE_TO_TIMER, this._enable.bind(this));
        app.appModeManager.on(app.EVENT_APP_MODE_TO_SUMMARY, this._disable.bind(this));
    };

    // Make timer and event names visible at app scope
    app.Timer = Timer;
    app.EVENT_TIMER_STOP     = EVENT_TIMER_STOP;
    app.EVENT_TIMER_START    = EVENT_TIMER_START;
    app.EVENT_TIMER_INTERVAL = EVENT_TIMER_INTERVAL;
    app.EVENT_TIMER_ARMED    = EVENT_TIMER_ARMED;

    app.debug_timer_state = debug_timer_state;
})();