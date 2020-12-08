(function () {

    var MOD_APPLY_DNF      = "apply_dnf";
    var MOD_APPLY_PLUS_TWO = "apply_plus_two";
    var MOD_CLEAR_PENALTY  = "clear_penalty";
    var MOD_DELETE_SOLVE   = "delete_solve";

    // To manage user settings for the UI
    window.app.userSettingsManager = new window.app.UserSettingsManager();

    // Clean-up stray whitespace from template rendering which makes the potential use of lettering.js below gross.
    $('.scram').text($('.scram').text().trim());

    var prepareSquanScramble = function() {
        // Chunk Sq-1 scrambles by (u,d) pairs and slice moves, separated by spaces, so lettering.js grabs each "move"
        // as a "word"
        if (window.app.eventName == 'Square-1') {
            var s = $('.scram').text();
            s = s.replaceAll(', ', ',');
            s= s.replaceAll('/', ' / ');
            $('.scram').text(s);
        }
    };

    // Immediately fit the scramble text to the scramble container, and setup a window resize callback to keep
    // performing that text resize on desktop.
    var fitText = function () {
        textFit($('.scram')[0], { multiLine: true, maxFontSize: 36 });
        if (window.app.doShowScramble) {
            $('.textFitted').lettering('words').children('span').addClass('partial_scramble');
        }
    };

    prepareSquanScramble();
    fitText();

    $(window).resize(fitText);

    var imageGenerator = null;

    // If this event supports scramble previews:
    // 1. initialize the scramble image generator, which will render the small-size scramble preview
    // 2. add a click/press handler on the preview to show the large scramble preview
    if (window.app.doShowScramble) {
        imageGenerator = new window.app.ScrambleImageGenerator();
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
    $('.btn_return_home').click(function() {
        window.location.href = '/';
    });

    // Arrange for modal for event info
    $('.event_description').click(function() {
        bootbox.alert({
            message: $(this).data('description'),
            centerVertical: true,
            closeButton: false,
        });
    })

    var wirePartialScramblePreviewEvents = function() {

        var resetScrambleTimeout;

        $('.partial_scramble').hover(function() {
            // Clear the timeout to reset the scramble back to full, so the full scramble
            // doesn't replace the partial scramble we're about to draw.
            clearTimeout(resetScrambleTimeout);

            // Figure out the index of the move being hovered over, and then get all moves up to and
            // including that one.
            var index = $(this).parent().children('.partial_scramble').index(this);
            var $scramble_pieces = $(this).parent().children('.partial_scramble').slice(0, index+1);

            // Mark them as 'engaged' to give them visual distinction
            $scramble_pieces.addClass('engaged');

            // Disengage other pieces of the scramble no longer highlighted
            var $remaining = $(this).parent().children('.partial_scramble').slice(index+1, $(this).parent().children('.partial_scramble').length);
            $remaining.removeClass('engaged');

            // Grab all the components of the scramble up to this point and join them together to get
            // the partial scramble
            var partial_scramble_to_render = $scramble_pieces
                                                .map(function() { return $(this).text(); })
                                                .get()
                                                .join(' ');

            // Render the partial scramble
            if (imageGenerator != null) {
                imageGenerator.replaceScramble(partial_scramble_to_render);
            }
        });

        $('.textFitted').mouseleave(function() {
            // Remove the visual distinction so the user knows they haven't highlighted any more
            $('.partial_scramble').removeClass('engaged');

            // Set a timeout to redraw the full scramble, if the user doesn't hover another move (and therefore cancel the timeout)
            // in the next little bit.
            if (imageGenerator != null) {
                resetScrambleTimeout = setTimeout(function() { imageGenerator.replaceScramble(window.app.scramble); }, 250);
            }
        });
    };

    wirePartialScramblePreviewEvents();

    // Update a button's state based on the button state info dict returned from the front end
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

    // Update the scramble text
    var updateScramble = function(scrambleText) {
        if (window.app.eventName == 'COLL') {
            $('.scram').html(scrambleText);
        } else {
            if (scrambleText.includes('\n')) {
                var parsedScramble = '';
                $.each(scrambleText.split('\n'), function (i, part) {
                    parsedScramble += part;
                    parsedScramble += '<br>';
                });
                $('.scram').html(parsedScramble);
            } else {
                $('.scram').html(scrambleText);
            }
        }
        prepareSquanScramble();
        fitText();
        wirePartialScramblePreviewEvents();
    };

    // Check if the selected solve has DNF penalty
    var hasDNF = function($solve_clicked) {
        // use attr() instead of data(), so we can replace the attribute value on an ajax
        // timer page reload. If we use data, jQuery doesn't update the value automatically
        // if the DOM changes
        return $solve_clicked.attr('data-is_dnf')  == 'true';
    };

    // Check if the selected solve has +2 penalty
    var hasPlusTwo = function($solve_clicked) {
        // use attr() instead of data(), so we can replace the attribute value on an ajax
        // timer page reload. If we use data, jQuery doesn't update the value automatically
        // if the DOM changes
        return $solve_clicked.attr('data-is_plus_two') == 'true';
    };

    // Modify the solve somehow; apply +2 or DNF, clear penalties, or delete the solve
    var applySolveModification = function($solve_clicked, modification) {
        var data = {};
        data.comp_event_id = window.app.compEventId;
        data.solve_id = parseInt($solve_clicked.attr('data-solve_id'));

        var route;
        switch (modification) {
            case MOD_APPLY_DNF:
                route = '/set_dnf';
                break;
            case MOD_APPLY_PLUS_TWO:
                route = '/set_plus_two';
                break;
            case MOD_CLEAR_PENALTY:
                route = '/clear_penalty';
                break;
            case MOD_DELETE_SOLVE:
                route = '/delete_solve';
                break;
            default:
                return;
        }

        $.ajax({
            url: route,
            type: "POST",
            data: JSON.stringify(data),
            contentType: "application/json",
            success: window.app.reRenderTimer,
            error: function (xhr) {
                bootbox.alert("Something unexpected happened: " + xhr.responseText);
            }
        });
    };

    // Copy the selected solve's scramble to the clipboard
    var copyScramble = function($solve_clicked) {
        var scramble = $solve_clicked.attr('data-scramble');
        var $temp = $("<input>");
        $("body").append($temp);
        $temp.val(scramble).select();
        document.execCommand("copy");
        $temp.remove();
    };

    var manualTimeEntry = function($solve_clicked) {
        $(document).on('input', '.bootbox-input.bootbox-input-text.form-control', function () {
            window.app.modifyTimeToProperFormat('.bootbox-input.bootbox-input-text.form-control');
        });

        var solveId = parseInt($solve_clicked.attr('data-solve_id'));

        bootbox.prompt({
            title: 'Input your time',
            centerVertical: true,
            callback: function (result) {
                // Dialog box was closed/canceled
                if (result == null) {
                    return;
                }

                var data = {};
                data.comp_event_id = window.app.compEventId;
                data.solve_id = solveId;
                data.elapsed_centiseconds = window.app.hmsToCentiseconds(result);

                $.ajax({
                    url: '/set_time',
                    type: "POST",
                    data: JSON.stringify(data),
                    contentType: "application/json",
                    success: window.app.reRenderTimer,
                    error: function (xhr) {
                        bootbox.alert("Something unexpected happened: " + xhr.responseText);
                    }
                });

                $(document).off('input', '.bootbox-input.bootbox-input-text.form-control');
            }
        });
    };

    var wireContextMenu = function() {

        var menuItems = {
            "clear": {
                name: "Clear penalty",
                icon: "far fa-thumbs-up",
                callback: function(itemKey, opt, e) { 
                    applySolveModification($(opt.$trigger), MOD_CLEAR_PENALTY); 
                },
                disabled: function(key, opt) { return !(hasDNF(this) || hasPlusTwo(this)); }
            },
            "dnf": {
                name: "DNF",
                icon: "fas fa-ban",
                callback: function(itemKey, opt, e) { 
                    applySolveModification($(opt.$trigger), MOD_APPLY_DNF); 
                },
                // TODO can I clean up this disabled function by just passing hasDNF directly? test
                disabled: function(key, opt) { return hasDNF(this); }
            },
            "plusTwo": {
                name: "+2",
                icon: "fas fa-plus",
                callback: function(itemKey, opt, e) { 
                    applySolveModification($(opt.$trigger), MOD_APPLY_PLUS_TWO); 
                },
                disabled: function(key, opt) { return hasPlusTwo(this); }
            },
            "sep1": "---------",
            "manual_entry": {
                name: "Manual time entry",
                icon: "fas fa-edit",
                callback: function(itemKey, opt, e) { manualTimeEntry($(opt.$trigger)); },
            },
            "sep2": "---------",
            "copy_scramble" : {
                name: "Copy scramble",
                icon: "fas fa-clipboard",
                callback: function(itemKey, opt, e) { copyScramble($(opt.$trigger)); }
            },
            "sep3": "---------",
            "delete": {
                name: "Delete time",
                icon: "fas fa-trash",
                callback: function(itemKey, opt, e) { 
                    applySolveModification($(opt.$trigger), MOD_DELETE_SOLVE); 
                },
            }
        };

        // If this is for FMC or MBLD, don't display the menu entries. for modifying solves
        // Also alter the delete menu text to say "delete solution" instead of "delete time"
        if (window.app.eventName == 'FMC' || window.app.eventName == 'MBLD') {
            delete menuItems.clear;
            delete menuItems.dnf;
            delete menuItems.plusTwo;
            delete menuItems.clear;
            delete menuItems.sep1;
            delete menuItems.manual_entry;
            delete menuItems.sep2;

            if (window.app.eventName == 'FMC') {
                menuItems.delete.name = "Delete solution";
            } else {
                delete menuItems.sep3;
                delete menuItems.copy_scramble;
                menuItems.delete.name = "Delete attempt";
            }
        }

        $.contextMenu({
            selector: '.single_time.ctx_menu',
            trigger: 'left',
            hideOnSecondTrigger: true,
            items: menuItems,
        });
    };

    wireContextMenu();

    // Function to re-render the timer page based on new event data after a successful
    // solve save, modification, delete, or comment change
    window.app.reRenderTimer = function(eventData) {
        eventData = JSON.parse(eventData);

        // Update scramble ID and scramble text fields in window.app data holder
        window.app.scrambleId = eventData['scramble_id'];
        window.app.scramble = eventData['scramble_text'];

        // Update the 'last solve' text stored locally, for delete confirmation
        window.app.lastResult = eventData['last_solve'];

        // Update the comment
        window.app.comment = eventData['comment'];

        // Update the isComplete flag and enable/disable visual elements as necessary
        window.app.isComplete = eventData['is_complete'];
        if (window.app.isComplete) {
            $('#the_manual_entry, #the_timer, #the_mbld_entry').addClass('disabled');
        } else {
            $('#the_manual_entry, #the_timer, #the_mbld_entry').removeClass('disabled');
        }

        // Render new scramble text and new scramble preview
        updateScramble(window.app.scramble);
        if (imageGenerator != null) {
            imageGenerator.prepareNewImage();
        }

        // Update the user solves text display in the sidebar / under the scramble text
        var userSolveDivs = $('.single_time').toArray();
        $.each(eventData['user_solves'], function(i, solveArray){
            var friendlyTime = solveArray[0];
            $(userSolveDivs[i]).html(friendlyTime);

            var solveId = solveArray[1];
            $(userSolveDivs[i]).attr('data-solve_id', solveId);
            if (solveId == -1) {
                $(userSolveDivs[i]).removeClass('ctx_menu');
            } else {
                $(userSolveDivs[i]).addClass('ctx_menu');
            }

            var isDnf = solveArray[2];
            var isPlusTwo = solveArray[3];
            $(userSolveDivs[i]).attr('data-is_dnf', isDnf);
            $(userSolveDivs[i]).attr('data-is_plus_two', isPlusTwo);

            var scramble = solveArray[4];
            $(userSolveDivs[i]).attr('data-scramble', scramble);
        });

        // Update the displayed time to match what's coming back from the server
        // for the most recent solve
        if (window.app.timerDisplayManager !== undefined) {
            var s = eventData['last_seconds'];
            var cs = eventData['last_centis'];
            var hideDot = eventData['hide_timer_dot'];
            window.app.timerDisplayManager._displayTime(s, cs, hideDot);
        }

        if (window.app.timer !== undefined) {
            // Reset the timer controller, if we are using the timer
            // and ensure the timer is either enabled or disabled depending
            // on whether the event is complete or not
            window.app.timer._reset();
            if (window.app.isComplete) {
                window.app.timer._disable();
            } else {
                window.app.timer._enable();
            }
        } else {
            // Otherwise clear the inputs for manual entry, MBLD, FMC
            $('#manualEntryInput, #successInput, #totalInput, #timeInput').val('');
        }
        
        // Update all the control button states
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