(function () {

    var scrambleId = window.app.scrambleId;
    var compEventId = window.app.compEventId;

    function isBlank(str) {
        return (!str || /^\s*$/.test(str));
    }

    function processResultsAndSubmit() {

        $('#totalInput, #successInput').on('input', modifyNumbersToProperFormat);
        $('#totalInput, #successInput').on('keypress', disallowNonDigits);

        var timeValue = $('#timeInput').val();
        if (isBlank(timeValue)) { return false; }

        var numAttempted  = $('#totalInput').val();
        var numSuccessful = $('#successInput').val();

        if (isBlank(numAttempted) || isBlank(numSuccessful)) { return false; }

        numAttempted = parseInt(numAttempted);
        numSuccessful = parseInt(numSuccessful);

        if (isNaN(numAttempted)) {
            bootbox.alert("Oops! " + numAttempted + " is not a valid number.");
            return false;
        }

        if (isNaN(numSuccessful)) {
            bootbox.alert("Oops! " + numSuccessful + " is not a valid number.");
            return false;
        }

        if (numSuccessful > numAttempted) {
            bootbox.alert("Oops! Successes higher than total attempted.<br>Check your numbers.");
            return false;
        }

        var isDnf = false;
        var numPoints = numSuccessful - (numAttempted - numSuccessful);
        var elapsedCentiseconds = window.app.hmsToCentiseconds(timeValue);
        var elapsedSeconds = (Math.floor(elapsedCentiseconds / 100));

        if (numPoints < 0) {
            isDnf = true;
        } else if ((numPoints == 0) && numAttempted == 2) {
            isDnf = true;
        }

        var solve_data = {};
        solve_data.scramble_id = scrambleId;
        solve_data.comp_event_id = compEventId;
        solve_data.is_dnf = isDnf;
        solve_data.is_plus_two = false;

        // coded results format is XXYYYYZZ
        // where XX   = (99 - number of points)
        // where YYYY = elapsed seconds (4 digits, padded with insignificant zeros)
        // where ZZ   = number missed (2 digits, padded with insignificant zeros)
        var XX = ('' + (99 - numPoints));
        var YYYY = ('' + elapsedSeconds).padStart(4, '0');
        var ZZ = ('' + (numAttempted - numSuccessful)).padStart(2, '0');
        var coded_integer_results = parseInt(XX + YYYY + ZZ);

        // We're hijacking this value, since MBLD can be represented in "coded integer" form and then results
        // just sorted by integer value
        solve_data.elapsed_centiseconds = coded_integer_results;

        var reload = function () { setTimeout(function () { window.location.reload(); }, 250); };

        $.ajax({
            url: '/post_solve',
            type: "POST",
            data: JSON.stringify(solve_data),
            contentType: "application/json",
            success: reload,
            error: function (xhr) {
                bootbox.alert("Something unexpected happened: " + xhr.responseText);
            }
        });

        return false;
    }

    function disallowNonDigits(event) {
        var regex = new RegExp("^[0-9]+$");
        var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
        if (!regex.test(key)) {
           event.preventDefault();
           return false;
        }
    };

    function modifyTimeToProperFormat() {
        var currentValue  = $('#timeInput').val();
        var valDigitsOnly = currentValue.replace(/[^0-9]/g, '');

        var currLength = valDigitsOnly.length;

        if (currLength <= 2) {
            $('#timeInput').val(valDigitsOnly);
        } else if (currLength > 2 && currLength <= 4) {
            var modified = valDigitsOnly.splice(currLength - 2, 0, '.');
            $('#timeInput').val(modified);
        } else if (currLength > 4) {
            var modified = valDigitsOnly.splice(currLength - 2, 0, '.');
            modified = modified.splice(modified.length - 5, 0, ':');
            $('#timeInput').val(modified);
        }
    }

    function modifyNumbersToProperFormat(e) {
        $(e.target).val('' + parseInt($(e.target).val()));
    }

    $('#timeInput').on('input', modifyTimeToProperFormat);
    $('#totalInput, #successInput').on('input', modifyNumbersToProperFormat);
    $('#totalInput, #successInput').on('keypress', disallowNonDigits);

    $('#mbldEntryForm,#mbldEntryForm2').submit(processResultsAndSubmit);

    $('#successInput').focus();
})();