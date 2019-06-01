(function(){

    // Immediately fit the scramble text to the scramble container, and setup a window resize callback to keep
    // performing that text resize on desktop.
    var fitText = function() { textFit($('.scram')[0], {multiLine: true, maxFontSize: 50}); };
    fitText();
    $(window).resize(fitText);

    // If this event supports scramble previews:
    // 1. initialize the scramble image generator, which will render the small-size scramble preview
    // 2. dd a click/press handler on the preview to show the large scramble preview
    // TODO: redraw scramble on window resize
    if (window.app.doShowScramble) {
        var imageGenerator = new window.app.ScrambleImageGenerator();
        $('.scramble_preview').click(function(){
            imageGenerator.showLargeImage();
            $('#fade-wrapper').fadeIn().addClass('shown');
            $('#fade-wrapper').click(function(){
                $(this).fadeOut(function(){
                    $(this).removeClass('shown');
                });
            });
        });
    }

    // Timer stuff
    // TODO comment better
    window.app.timer = new window.app.Timer(window.app.eventName, window.app.scrambleId, window.app.compEventId);
    window.app.timerDisplayManager = new window.app.TimerDisplayManager();

    var reload = function () { setTimeout(function () { window.location.reload(); }, 250); };

    // Wire up the undo button
    $('#BTN_UNDO').click(function(){
        var confirm_msg = "Are you sure you want to delete your last solve? (" + window.app.lastResult + ")";
        bootbox.confirm({
            message: confirm_msg,
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
                    success: reload,
                    error: function(xhr) {
                        alert("Something unexpected happened: " + xhr.responseText);
                    }
                });
            }
        });
    });

    // Wire up the +2 button
    $('#BTN_PLUS_TWO').click(function(){

        var data = {};
        data.comp_event_id = window.app.compEventId;

        $.ajax({
            url: '/toggle_prev_plus_two',
            type: "POST",
            data: JSON.stringify(data),
            contentType: "application/json",
            success: reload,
            error: function(xhr) {
                alert("Something unexpected happened: " + xhr.responseText);
            }
        });
    });

    // Wire up the DNF button
    $('#BTN_DNF').click(function(){

        var data = {};
        data.comp_event_id = window.app.compEventId;

        $.ajax({
            url: '/toggle_prev_dnf',
            type: "POST",
            data: JSON.stringify(data),
            contentType: "application/json",
            success: reload,
            error: function(xhr) {
                alert("Something unexpected happened: " + xhr.responseText);
            }
        });
    });

})();