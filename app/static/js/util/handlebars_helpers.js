(function() {
    // Increments the supplied integer by 1
    Handlebars.registerHelper("inc", function(value, options){ return parseInt(value) + 1; });

    // Compares two values for equality
    Handlebars.registerHelper("eq", function(a, b, options){ return a == b; });

    // Returns a user-friendly representation of the supplied centiseconds
    // The argument to this is a "solve" object which contains a raw time in centiseconds,
    // and status flags for DNF and +2 penalties
    Handlebars.registerHelper("renderTime", window.app.renderTime);

    // General-purpose Handlebars helper for performing mathematical operations.
    Handlebars.registerHelper("math", function(lvalue, operator, rvalue, options) {
        if (arguments.length < 4) {
            // Operator omitted, assuming "+"
            options = rvalue;
            rvalue = operator;
            operator = "+";
        }

        lvalue = parseFloat(lvalue);
        rvalue = parseFloat(rvalue);

        return {
            "+": lvalue + rvalue,
            "-": lvalue - rvalue,
            "*": lvalue * rvalue,
            "/": lvalue / rvalue,
            "%": lvalue % rvalue
        }[operator];
    });

    // Converts the value coming in to an integer, then returns the string representation
    Handlebars.registerHelper("int_str", function(value, options){ return "" + parseInt(value); });
})();