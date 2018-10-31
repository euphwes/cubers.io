(function() {

    /**
     * Converts an integer number of seconds into a string denoting minutes and seconds.
     * Ex: 120 --> 2:00
     *      90 --> 1:30
     *      65 --> 1:05
     *      51 -->   51
     *       9 -->    9
     */
    function convertSecondsToMinutes(seconds) {
        var s = parseFloat(seconds);

        var minutes = Math.floor(s / 60);
        var seconds = s % 60;

        if (minutes > 0) {
            return minutes + ':' + ("" + seconds).padStart(2, "0");
        } else {
            return seconds;
        }
    };

    /**
     * Converts a time string (ss.xx, mm:ss.xx, hh:mm:ss.xx) to just centiseconds.
     */
    function hmsToCentiseconds(str) {

        var cs = 0;
        var p = '';
    
        var cs_parts = str.split(".");
        if (cs_parts.length > 1) {
            cs_str = cs_parts.pop(-1);
            if (cs_str.length == 1) {
                cs_str += "0";
            }
            if (cs_str.length > 2) {
                cs_str = cs_str.substring(0, 2);
            }
            cs = parseInt(cs_str);
            p = cs_parts[0].split(':');
        } else {
            p = str.split(':');
        }
    
        var s = 0;
        var m = 1;
    
        while (p.length > 0) {
            s += m * parseInt(p.pop(), 10);
            m *= 60;
        }
    
        return (s * 100) + cs;
    };
    
    /**
     * Converts an integer number of centiseconds to a string representing the
     * time in minutes, seconds, and centiseconds for use in a timer panel solve card.
     *
     * Ex: 1234 -->   12.34
     *      600 -->    6.00
     *     7501 --> 1:15.01
     *    13022 --> 2:10.22
     */
    function convertRawCsForSolveCard(value, plusTwo){
        plusTwo = plusTwo || false; // default value of false

        var cs = parseInt(value);
        if (plusTwo) { cs += 200; }

        var s = Math.floor(cs / 100);
        var remainingCs = cs % 100;
        return "" + convertSecondsToMinutes(s) + "." + ("" + remainingCs).padStart(2, "0");
    };

    /**
     * Converts a string to a boolean based on the value of the string, not the presence of the string.
     *
     * Ex: "0" --> false
     *     "1" --> true
     *  "true" --> true
     *  "TRUE" --> true
     * "false" --> false
     * "FALSE" --> false
     */
    function evaluateBool(val) {
        return !!JSON.parse(String(val).toLowerCase());
    };

    /**
     * Renders a solve time as a human-friendly string, based on penalty status and raw solve time.
     */
    function renderTime(solve) {
        if (solve.isDNF) {
            return "DNF";
        }
        if (solve.isPlusTwo) {
            return convertRawCsForSolveCard(solve.time, true) + "+";
        }
        return convertRawCsForSolveCard(solve.time);
    };

    // Make these util functions all available at the app scope
    window.app.convertSecondsToMinutes = convertSecondsToMinutes;
    window.app.convertRawCsForSolveCard = convertRawCsForSolveCard;
    window.app.evaluateBool = evaluateBool;
    window.app.renderTime = renderTime;
    window.app.hmsToCentiseconds = hmsToCentiseconds;
})();