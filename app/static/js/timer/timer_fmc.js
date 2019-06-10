(function () {

    // TODO: comment me plz

    function disallowNonDigitsAndDNF(event) {
        var regex = new RegExp("^[0-9DNFdnf]+$");

        var rawCode = !event.charCode ? event.which : event.charCode;
        if (rawCode == 13) { return true; }

        var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
        if (!regex.test(key)) {
           event.preventDefault();
           return false;
        }
    };

    function verifyAndProcessFMCEntry() {
        var currentValue = $('#manualEntryInput').val();
        var isDNF = false;
        var asInt = 99900;

        var showInvalid = function() {;
            bootbox.alert('"' + currentValue + '" is not a valid result!<br>Please enter "DNF" or number of moves.');
        }

        if (currentValue.toUpperCase() == 'DNF') {
            isDNF = true;
        } else {
            if (currentValue.includes('.') || currentValue.includes(':')) {
                showInvalid();
                return false;
            }
            try {
                asInt = parseInt(currentValue) * 100;
                if (isNaN(asInt)) {
                    showInvalid();
                    return false;
                }
            } catch (error) {
                showInvalid();
                return false;
            }
        }

        var solve_data = {};
        solve_data.scramble_id = window.app.scrambleId;
        solve_data.comp_event_id = window.app.compEventId;
        solve_data.is_dnf = isDNF;
        solve_data.is_plus_two = false;

        if (solve_data.is_dnf) {
            solve_data.elapsed_centiseconds = 99900;
        } else {
            solve_data.elapsed_centiseconds = asInt;
        }

        $.ajax({
            url: '/post_solve',
            type: "POST",
            data: JSON.stringify(solve_data),
            contentType: "application/json",
            success: window.app.reRenderTimer,
            error: function (xhr) {
                bootbox.alert("Something unexpected happened: " + xhr.responseText);
            }
        });

        return false;
    }

    $('#manualEntryInput').on('keypress', disallowNonDigitsAndDNF);

    $('#manualEntryForm').submit(verifyAndProcessFMCEntry);
    $('#manualEntryInput').focus();
})();