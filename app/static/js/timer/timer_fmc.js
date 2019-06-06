(function () {

    // TODO: comment me plz

    var scrambleId = window.app.scrambleId;
    var compEventId = window.app.compEventId;

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
        solve_data.scramble_id = scrambleId;
        solve_data.comp_event_id = compEventId;
        solve_data.is_dnf = isDNF;
        solve_data.is_plus_two = false;

        if (solve_data.is_dnf) {
            solve_data.elapsed_centiseconds = 99900;
        } else {
            solve_data.elapsed_centiseconds = asInt;
        }


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

    $('#manualEntryForm').submit(verifyAndProcessFMCEntry);
    $('#manualEntryInput').focus();
})();