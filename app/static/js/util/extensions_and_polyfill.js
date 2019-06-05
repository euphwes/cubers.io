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

    if (!String.prototype.splice) {
        /**
         * {JSDoc}
         *
         * The splice() method changes the content of a string by removing a range of
         * characters and/or adding new characters.
         *
         * @this {String}
         * @param {number} start Index at which to start changing the string.
         * @param {number} delCount An integer indicating the number of old chars to remove.
         * @param {string} newSubStr The String that is spliced in.
         * @return {string} A new string with the spliced substring.
         */
        String.prototype.splice = function (start, delCount, newSubStr) {
            return this.slice(0, start) + newSubStr + this.slice(start + Math.abs(delCount));
        };
    }

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

    jQuery.fn.disableTextSelect = function() {
        return this.each(function() {
            $(this).css({
                'MozUserSelect':'none',
                'webkitUserSelect':'none'
            }).attr('unselectable','on').bind('selectstart', function() {
                return false;
            });
        });
    };
    
    jQuery.fn.enableTextSelect = function() {
        return this.each(function() {
            $(this).css({
                'MozUserSelect':'',
                'webkitUserSelect':''
            }).attr('unselectable','off').unbind('selectstart');
        });
    };
})();