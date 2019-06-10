(function () {

    // TODO: comment me plz

    var scrambleId = window.app.scrambleId;
    var compEventId = window.app.compEventId;

    function isBlank(str) {
        return (!str || /^\s*$/.test(str));
    }

    function verifyAndProcessManualTime() {

        var currentValue = $('#manualEntryInput').val();
        if (isBlank(currentValue)) { return false; }

        var solve_data = {};
        solve_data.scramble_id = scrambleId;
        solve_data.comp_event_id = compEventId;
        solve_data.is_dnf = false;
        solve_data.is_plus_two = false;
        solve_data.elapsed_centiseconds = window.app.hmsToCentiseconds(currentValue);

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

    $('#manualEntryInput').on('input', function () { window.app.modifyTimeToProperFormat('#manualEntryInput'); });
    $('#manualEntryForm').submit(verifyAndProcessManualTime);

    $('#manualEntryInput').focus();
})();