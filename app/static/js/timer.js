(function() {

    var EVENT_TIMER_START    = 'event_timer_start';
    var EVENT_TIMER_INTERVAL = 'event_timer_interval';
    var EVENT_TIMER_STOP     = 'event_timer_stop';
    var EVENT_TIMER_ATTACHED = 'event_timer_attached';
    var EVENT_TIMER_RESET    = 'event_timer_reset';

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
    };
    Timer.prototype = Object.create(window.app.EventEmitter.prototype);

    /**
     * "Attach" the timer to a specific scrambleId so it can send appropriate data when
     * it emits events.
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
    Timer.prototype.start = function() {
        this.startTime = new Date();
        this.timerInterval = setInterval(this.timerIntervalFunction.bind(this), 42);
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
    Timer.prototype.stop = function() {
    
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
    Timer.prototype.reset = function() {
        clearInterval(this.timerInterval);
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
    Timer.prototype.timerIntervalFunction = function() {
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
})();