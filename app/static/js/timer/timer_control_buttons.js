(function () {

    // Wire up the undo button
    $('#BTN_UNDO').click(function () {
        var confirm_msg = "Are you sure you want to delete your last solve? (" + window.app.lastResult + ")";
        bootbox.confirm({
            message: confirm_msg,
            centerVertical: true,
            buttons: {
                confirm: {
                    label: 'Yes',
                    // className: 'btn-success'
                },
                cancel: {
                    label: 'Cancel',
                    // className: 'btn-danger'
                }
            },
            callback: function (result) {
                if (!result) { return; }

                var data = {};
                data.comp_event_id = window.app.compEventId;

                $.ajax({
                    url: '/delete_prev_solve',
                    type: "POST",
                    data: JSON.stringify(data),
                    contentType: "application/json",
                    success: window.app.reRenderTimer,
                    error: function (xhr) {
                        alert("Something unexpected happened: " + xhr.responseText);
                    }
                });
            }
        });
    });

    // Wire up the +2 button
    $('#BTN_PLUS_TWO').click(function () {

        var data = {};
        data.comp_event_id = window.app.compEventId;

        $.ajax({
            url: '/toggle_prev_plus_two',
            type: "POST",
            data: JSON.stringify(data),
            contentType: "application/json",
            success: window.app.reRenderTimer,
            error: function (xhr) {
                alert("Something unexpected happened: " + xhr.responseText);
            }
        });
    });

    // Wire up the DNF button
    $('#BTN_DNF').click(function () {

        var data = {};
        data.comp_event_id = window.app.compEventId;

        $.ajax({
            url: '/toggle_prev_dnf',
            type: "POST",
            data: JSON.stringify(data),
            contentType: "application/json",
            success: window.app.reRenderTimer,
            error: function (xhr) {
                alert("Something unexpected happened: " + xhr.responseText);
            }
        });
    });

    // Wire up the comment button
    $('#BTN_COMMENT').click(function () {

        // disable the timer so the key/space events here don't trigger the timer starting
        if (!window.app.isComplete) {
            if (window.app.timer !== undefined) {
                window.app.timer._disable();
            }
        }

        bootbox.prompt({
            title: 'Comment for ' + window.app.eventName,
            value: window.app.comment,
            inputType: "textarea",
            centerVertical: true,
            buttons: {
                confirm: {
                    label: 'Update comment',
                    // className: 'btn-success'
                },
                cancel: {
                    label: 'Cancel',
                    // className: 'btn-danger'
                }
            },
            callback: function (result) {
                if (result == null) {
                    // Dialog box was closed/canceled, so don't update comment, and re-enable the timer
                    if (!window.app.isComplete) {
                        if (window.app.timer !== undefined) {
                            window.app.timer._enable();
                        } 
                    }
                    return;
                }

                var data = {};
                data.comp_event_id = window.app.compEventId;
                data.comment = result;

                $.ajax({
                    url: '/apply_comment',
                    type: "POST",
                    data: JSON.stringify(data),
                    contentType: "application/json",
                    success: window.app.reRenderTimer,
                    error: function (xhr) {
                        alert("Something unexpected happened: " + xhr.responseText);
                    }
                });
            }
        });
    });

})();