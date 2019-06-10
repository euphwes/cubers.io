(function () {

    // To manage user settings for the UI
    window.app.userSettingsManager = new window.app.UserSettingsManager();

    // Immediately fit the scramble text to the scramble container, and setup a window resize callback to keep
    // performing that text resize on desktop.
    var fitText = function () { textFit($('.scram')[0], { multiLine: true, maxFontSize: 50 }); };
    fitText();
    $(window).resize(fitText);

    // If this event supports scramble previews:
    // 1. initialize the scramble image generator, which will render the small-size scramble preview
    // 2. dd a click/press handler on the preview to show the large scramble preview
    // TODO: redraw scramble on window resize
    if (window.app.doShowScramble) {
        var imageGenerator = new window.app.ScrambleImageGenerator();
        $('.scramble_preview:not(.no_pointer),.btn_scramble_preview').click(function () {
            imageGenerator.showLargeImage();
            $('#fade-wrapper').fadeIn().addClass('shown');
            $('#fade-wrapper').click(function () {
                $(this).fadeOut(function () {
                    $(this).removeClass('shown');
                });
            });
        });
    }

    // Arrange for the 'return to events' button to navigate back to the main page
    $('.btn_return_home').click(function(){
        window.location.href = '/';
    });

    var updateButtonState = function(btnId, btnKey, buttonStateInfo) {
        if (buttonStateInfo[btnKey]['btn_active']) {
            $(btnId).addClass('active');
        } else {
            $(btnId).removeClass('active');
        }
        if (buttonStateInfo[btnKey]['btn_enabled']) {
            $(btnId).removeAttr("disabled");
        } else {
            $(btnId).attr('disabled', 'disabled');
        }
    };

    // Function to re-render the timer page based on new event data after a successful
    // solve save, modification, delete, or comment change
    window.app.reRenderTimer = function(eventData) {
        // 'button_state_info': button_state_info,
        //     'scramble_text': scramble_text,
        //         'scramble_id': scramble_id,
        //             'user_solves': user_solves,
        //                 'last_seconds': last_seconds,
        //                     'last_centis': last_centis,
        //                         'hide_timer_dot': hide_timer_dot,
        //                             'is_complete': is_complete,
        //                                 'comment': comment,
        eventData = JSON.parse(eventData);
        
        var buttonStateInfo = eventData['button_state_info'];
        updateButtonState('#BTN_DNF', 'btn_dnf', buttonStateInfo);
        updateButtonState('#BTN_UNDO', 'btn_undo', buttonStateInfo);
        updateButtonState('#BTN_COMMENT', 'btn_comment', buttonStateInfo);
        updateButtonState('#BTN_PLUS_TWO', 'btn_plus_two', buttonStateInfo);
        
    }

    // A helper function to auto-format times in text input fields to the following format
    // 0:00.00 placeholder for empty times
    // 00.12   for fractional seconds
    // 12.34   for seconds and fractions
    // 1:23.45 for minutes and seconds
    window.app.modifyTimeToProperFormat = function(inputId) {

        // Get the current value out of the input, and strip all characters except for digits out
        var currentValue = $(inputId).val();
        var valDigitsOnly = currentValue.replace(/[^0-9]/g, '');

        // Strips leading zeros to ensure a clean slate of user-entered time digits
        while (valDigitsOnly.startsWith('0')) {
            valDigitsOnly = valDigitsOnly.substring(1, valDigitsOnly.length);
        }

        // If the number of digits is less than or equal to 3, left-pad with 0 until the total
        // string is four digits long (so sub-minute times will fit into 00.00 format)
        if (valDigitsOnly.length <= 3) {
            while (valDigitsOnly.length <= 3) { valDigitsOnly = '0' + valDigitsOnly; }
        }

        var currLength = valDigitsOnly.length;
        var modified   = '';

        if (currLength <= 4) {
            // If the raw time digits are less than four digits long, insert a decimal
            // to properly separate seconds from centiseconds.
            modified = valDigitsOnly.splice(currLength - 2, 0, '.');
            if (modified == '00.00') {
                // If the modified input value is 00.00 exactly, the user has deleted all digits,
                // so let's just empty the input so the placeholder is displayed.
                modified = '';
            }
        } else if (currLength > 4) {
            // If the raw time has more than four digits, insert both the colon and decimal into
            // the appropriate locations so the time reads as <min>:<sec>.<centis>
            modified = valDigitsOnly.splice(currLength - 2, 0, '.');
            modified = modified.splice(modified.length - 5, 0, ':');
        }

        $(inputId).val(modified);
    }
})();