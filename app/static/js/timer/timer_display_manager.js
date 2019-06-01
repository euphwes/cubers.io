(function() {
    var app = window.app;

    /**
     * Manages the state of the visible timer display based on events emitted by the timer
     */
    function TimerDisplayManager() {
        this._registerTimerEventHandlers();
    }

    /**
     * Displays the specified time on the timer display.
     */
    TimerDisplayManager.prototype._displayTime = function(seconds, centiseconds, hideDot) {
        var $dot = $('#dot');
        var $seconds = $('#seconds');
        var $centiseconds = $('#centiseconds');

        hideDot = hideDot || false; // default value of false

        if (!hideDot) {
            $dot.html('.');
        } else {
            $dot.html('');
        }

        $seconds.html(seconds);
        $centiseconds.html(centiseconds);
    };

    /**
     * Show all zeros.
     */
    TimerDisplayManager.prototype._showZero = function() {     
        this._displayTime("0", "00");
    };

    /**
     * Event handler for the timer's stop event - updates display time
     */
    TimerDisplayManager.prototype._handleTimerStop = function(timerStopData) {
        if (timerStopData.is_dnf) {
            this._displayTime("DNF", "", true);
        } else {
            this._displayTime(timerStopData.friendly_seconds, timerStopData.friendly_centiseconds);
        }
    };

    /**
     * Event handler for the timer's start event - updates display time
     */
    TimerDisplayManager.prototype._handleTimerStart = function () {
        $('.timer_text').removeClass('armed');
        if (app.userSettingsManager.get_setting(app.Settings.HIDE_RUNNING_TIMER)) {
            $('.timer_text').addClass('hidden');
        }
    };

    /**
     * Event handler for the timer's armed event
     */
    TimerDisplayManager.prototype._handleTimerArmed = function () {
        $('.timer_text').addClass('fullscreen');
        $('.timer_text').addClass('armed');
        $('.controls_wrapper').addClass('disabled');
        this._showZero();
    };

    /**
     * Event handler for the timer's inspection armed event
     */
    TimerDisplayManager.prototype._handleInspectionArmed = function () {
        $('.timer_text').addClass('armed');
        if (app.userSettingsManager.get_setting(app.Settings.HIDE_INSPECTION_TIME)) {
            $('.timer_text').removeClass('hidden');
        }
    };

    /**
     * Event handler for the timer's interval event - updates display time
     */
    TimerDisplayManager.prototype._handleTimerInterval = function(intervalData) {
        this._displayTime(intervalData.friendly_seconds, intervalData.friendly_centiseconds);
    };

    /**
     * Event handler for the timer's inspection countdown event - updates time remaining
     */
    TimerDisplayManager.prototype._handleInspectionInterval = function(intervalData) {
        this._displayTime(intervalData.seconds_remaining, "", true);
    };

    /**
     * Event handler for the timer starting inspection time
     */
    TimerDisplayManager.prototype._handleInspectionStarted = function(inspectionStartingSeconds) {
        $('.timer_text').removeClass('armed');
        if (app.userSettingsManager.get_setting(app.Settings.HIDE_INSPECTION_TIME)) {
            $('.timer_text').addClass('hidden');
        } else {
            this._displayTime(inspectionStartingSeconds, "", true);
        }
    };

    /**
     * Register handlers for timer events.
     */
    TimerDisplayManager.prototype._registerTimerEventHandlers = function() {
        app.timer.on(app.EVENT_TIMER_STOP, this._handleTimerStop.bind(this));
        app.timer.on(app.EVENT_TIMER_START, this._handleTimerStart.bind(this));
        app.timer.on(app.EVENT_TIMER_ARMED, this._handleTimerArmed.bind(this));
        app.timer.on(app.EVENT_INSPECTION_ARMED, this._handleInspectionArmed.bind(this));
        app.timer.on(app.EVENT_TIMER_INTERVAL, this._handleTimerInterval.bind(this));
        app.timer.on(app.EVENT_INSPECTION_INTERVAL, this._handleInspectionInterval.bind(this));
        app.timer.on(app.EVENT_INSPECTION_STARTED, this._handleInspectionStarted.bind(this));
        app.timer.on(app.EVENT_TIMER_CANCELLED, function() {
            this._showZero.bind(this)();
            $('.timer_text').removeClass('fullscreen');
            $('.timer_text').removeClass('hidden');
            $('.controls_wrapper').removeClass('disabled');
        }.bind(this) );
    };
    app.TimerDisplayManager = TimerDisplayManager;
})();