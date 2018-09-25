(function() {
    // inc: increments the supplied integer by 1
    Handlebars.registerHelper("inc", function(value, options){ return parseInt(value) + 1; });

    // eq: compares two values for equality
    Handlebars.registerHelper("eq", function(a, b, options){ return a == b; });

    // renderTime: returns a user-friendly representation of the supplied centiseconds
    Handlebars.registerHelper("renderTime", window.app.renderTime);

    // General-purpose handlebars helper for performing mathematical operations.
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