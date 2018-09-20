(function() {
    /**
     * Interpret the number as milliseconds and return the number of
     * whole seconds it represents as a string
     *
     * Ex: 1234 -->  1
     *     2000 -->  2
     *     2001 -->  2
     *    75777 --> 75
     */
    Number.prototype.getSecondsFromMs = function(){
        return ("" + Math.floor(this / 1000));
    };

    /**
     * Interpret the number as milliseconds and return the number of
     * centiseconds remaining after whole seconds are removed, as a string
     * and left-padded with zeros for a total length of 2
     *
     * Ex: 1234 --> 23
     *     2000 --> 00
     *     2001 --> 00
     *    75777 --> 77
     */
    Number.prototype.getTwoDigitCentisecondsFromMs = function(){
        return ("" + this % 1000).slice(0, -1).padStart(2, "0");
    };

    /**
     * Shows or hides the element via the ultra-hidden CSS class.
     * This different than $('thing').hide() or $('thing').show, because that uses `visibility: visible/hidden`
     * which still takes up space, whereas `.ultra-hidden` uses `display: none` which does not take up space
     */
    $.fn.extend({
        ultraHide: function(){ $(this).addClass('ultra-hidden'); },
        ultraShow: function(){ $(this).removeClass('ultra-hidden'); },
    });

    // https://github.com/uxitten/polyfill/blob/master/string.polyfill.js
    // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/padStart
    if (!String.prototype.padStart) {
        String.prototype.padStart = function padStart(targetLength,padString) {
            targetLength = targetLength>>0; //truncate if number or convert non-number to 0;
            padString = String((typeof padString !== 'undefined' ? padString : ' '));
            if (this.length > targetLength) {
                return String(this);
            }
            else {
                targetLength = targetLength-this.length;
                if (targetLength > padString.length) {
                    padString += padString.repeat(targetLength/padString.length); //append to original to ensure we are longer than needed
                }
                return padString.slice(0,targetLength) + String(this);
            }
        };
    }
    
})();