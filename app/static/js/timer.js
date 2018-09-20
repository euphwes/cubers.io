(function() {

    /**
     * Represents a timer which records times for a specific competition event.
     */
    var Timer = function(){
        window.app.EventEmitter.call(this);  // this Timer is an EventEmitter

        this.$seconds = $('#seconds');
        this.$centiseconds = $('#centiseconds');
        this.$dot = $('#dot');
        this.$singleSolveTimeElem = null;

        this.startTime = 0;
        this.elapsedTime = 0;
        this.timerInterval = null;
    };
    Timer.prototype = Object.create(window.app.EventEmitter.prototype);

    /**
     * "Attach" the timer to a specific solve time element so it knows where to store
     * the results when the timer is stopped. 
     */
    Timer.prototype.attach = function(solveTimeElem) {
        this.$singleSolveTimeElem = solveTimeElem;
        this.$singleSolveTimeElem.addClass('active');
        var newScramble = this.$singleSolveTimeElem.data('scramble');

        var renderedScramble = "";
        $.each(newScramble.split('\n'), function(i, piece){
            renderedScramble += "<p>" + piece + "</p>";
        });

        var $scrambleHolder = $('.scramble-wrapper>div');
        $scrambleHolder.html(renderedScramble);
    };
 
    /**
     * Starts the timer. Captures the start time so we can determine elapsed time on
     * subsequent ticks.
     */
    Timer.prototype.start = function() {
        this.startTime = new Date();
        this.$dot.html('.');
        this.timerInterval = setInterval(this.timerIntervalFunction.bind(this), 10);
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
        var full_time = window.app.convertSecondsToMinutes(s) + "." + cs;

        // ensure the timer display shows the same time as the solve card
        this.$seconds.html(window.app.convertSecondsToMinutes(s));
        this.$centiseconds.html(cs);

        // mark the attached solve card as complete and no longer active, set the solve time on
        // the card, and set the data attribute for raw time in centiseconds
        this.$singleSolveTimeElem.addClass('complete').removeClass('active');
        this.$singleSolveTimeElem.find('.time-value').html(full_time);
        this.$singleSolveTimeElem.attr("data-rawTimeCentiseconds", parseInt(s*100) + parseInt(cs))
        this.$singleSolveTimeElem.attr("data-isPlusTwo", "false")
        this.$singleSolveTimeElem.attr("data-isDNF", "false")
    };

    /**
     * Resets the timer, clearing start and elapsed time, and sets the visible timer elements
     * to the zero state.
     */
    Timer.prototype.reset = function() {
        clearInterval(this.timerInterval);
        this.startTime = 0;
        this.elapsedTime = 0;
        this.$seconds.html('0');
        this.$dot.html('.');
        this.$centiseconds.html('00');
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

        this.$seconds.html(window.app.convertSecondsToMinutes(s));
        this.$centiseconds.html(cs);
    };

    window.app.Timer = Timer;
})();