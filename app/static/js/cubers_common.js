var selectedScramble = null;
var selectedEvent = null;
var isDNF = false;
var isPlusTwo = false;

var events = {};

// ((..)|(..)|(..)...) is multiple alternatives
// First group checks for any number of digits (\d+), a :, exactly 2 digits (d{2}), a decimal, and one or more digits (\d+)
// Second group checks for any number of digits, a :, exactly two digits that are not followed by only a period ((?!.)).
// Third group checks for any number of digits followed by a period followed by any number of digits
// Fourth group checks for any number of digits that are not followed by only a period.
// Fifth group checks for DNF.
// The ^ and $ make sure that the ENTIRE string matches this regex. It means "from the beginning to end of string".
var timeInputRegex = new RegExp(/^(^\d+:\d{2}\.\d+$)|(^\d+:\d{2}(?!.)$)|(^\d*\.\d+$)|(^\d+(?!.)$)|(DNF)$/);

function selectScramble(scramble) {
    if (selectedScramble != null) {
        selectedScramble.$element.removeClass("active");
    }

    if (scramble != null) {
        selectedScramble = scramble
        scramble.$element.addClass("active");

        $("#btn-dnf").removeClass("disabled").removeClass("pressed");
        $("#btn-plus-two").removeClass("disabled").removeClass("pressed");
        $("#btn-enter-time").removeClass("disabled")
        $("#input-time").attr("placeholder", "Time for Scramble " + scramble.num).attr("aria-label", "Time for Scramble " + scramble.num).prop("disabled", false);

        setTimeout(function() {
            $("#input-time").focus();
        }, 50);
    } else {
        // We've reached the last scramble, or we don't want any selected.
        selectedScramble = null;
        $("#input-time").attr("placeholder", "Please select a scramble").prop("disabled", true);
        $("#btn-enter-time").addClass("disabled");
        $("#btn-dnf").addClass("disabled").removeClass("pressed");
        $("#btn-plus-two").addClass("disabled").removeClass("pressed");
    }

    isPlusTwo = false;
    isDNF = false;
}

function getScramble(scrambleId) {
    keys = Object.keys(events);

    for (var i = 0; i < keys.length; i++) {
        event = events[keys[i]];

        for (var j = 0; j < event.length; j++) {
            scramble = event[j];

            if (scramble.id == scrambleId) {
                return scramble;
            }
        }
    }

    return null;
}

function getNextScramble(event) {
    for (var i = 0; i < event.length; i++) {
        var scramble = event[i];

        if (scramble.time == 0) {
            return scramble;
        }
    }

    return null;
}

function addEvent(eventId) {
    events[eventId] = [];
}

function addScramble(eventId, scrambleId) {
    events[eventId].push({ id: scrambleId, time: 0, plusTwo: false, isDNF: false, num: events[eventId].length + 1, $element: $(".scrambles .scramble[data-scramble-id=" + scrambleId + "]")});
}

function onTabSwitch(eventId) {
    selectedEvent = events[eventId]

    selectScramble(getNextScramble(selectedEvent));
    $("#input-time").val("");
}

function setTimeInputValid(flag) {
    if (flag) {
        $("#input-time").removeClass("is-invalid");
    } else {
        $("#input-time").addClass("is-invalid");
    }
}

function convertMinutestoSeconds(timeString) {
    var parts = timeString.split(":");

    if (parts.length <= 1 || parseFloat(parts[1]) >= 60) {
        // If we're in minute format, the seconds can't be over 60 (aka 12 minutes and 76 seconds doesn't make sense)
        return Number.NaN;
    }
    console.log(parseInt(parts[0]) * 60 + parseFloat(parts[1]));
    return parseInt(parts[0]) * 60 + parseFloat(parts[1])
}

function convertSecondsToMinutes(time) {
    if (time < 60) {
        return time.toFixed(3);
    } else {
        var mins = Math.floor(time / 60);
        var secs = (time - mins * 60).toFixed(3);

        if (secs.length == 5) {
            secs = "0".concat(secs);
        }

        return mins + ":" + secs;
    }
}

function enterTime(scramble, time) {
    if (scramble == null || $("#btn-enter-time").hasClass("disabled")) {
        return;
    }

    if (timeInputRegex.test(time)) {
        setTimeInputValid(true);
    } else {
        setTimeInputValid(false);
        return;
    }

    scramble.isDNF = isDNF;
    scramble.isPlusTwo = isPlusTwo;

    if (time != "DNF") {
        if (time.indexOf(":") > -1) {
            time = convertMinutestoSeconds(time);
        } else {
            time = parseFloat(time);
        }

        if (isNaN(time)) {
            setTimeInputValid(false);
            return;
        }

        if (isPlusTwo) {
            time += 2.0;
        }

        scramble.$element.removeClass("dnf");
        scramble.$element.find(".scramble-time").html(convertSecondsToMinutes(time));
    } else {
        scramble.$element.addClass("dnf");
        scramble.$element.find(".scramble-time").html("DNF");
    }

    if (isPlusTwo) {
        scramble.$element.addClass("plus-two");
    } else {
        scramble.$element.removeClass("plus-two");
    }

    scramble.time = time;
    scramble.$element.addClass("solved");

    selectScramble(getNextScramble(selectedEvent));
    $("#input-time").val("");
}

$(document).ready(function() {
    $(".scramble").click(function() {
        selectScramble(getScramble($(this).data("scrambleId")));
    });

    $(".event-tab").click(function() {
        onTabSwitch($(this).data("competitionEventId"));
    })

    $("#btn-enter-time").click(function() {
        enterTime(selectedScramble, $("#input-time").val());
    });

    $("#input-time").on('keypress', function (e) {
        // First () is whether it is keys 0-9. 8 and 46 are backspace and delete.
        
        console.log(e.which + " " + e.shiftKey + " '" + String.fromCharCode(e.which) + "'");
        if (!((e.which >= 48 && e.which <= 57) || (String.fromCharCode(e.which) == ".") || (String.fromCharCode(e.which) == ":") || (e.which == 8) | (e.which == 46))) {
            e.preventDefault();
        } else if (e.which == 13) { // Enter key
            enterTime(selectedScramble, $("#input-time").val());
        } else {
            setTimeout(function() {
                if (timeInputRegex.test($("#input-time").val())) {
                    setTimeInputValid(true);
                } else {
                    setTimeInputValid(false);
                }
            }, 50);
        }
    });

    $("#btn-dnf").click(function() {
        if ($(this).hasClass("disabled")) {
            return;
        }

        isDNF = !isDNF;

        if (isDNF) {
            $("#input-time").prop("disabled", true).val("DNF");
            $(this).addClass("pressed");
            $("#btn-plus-two").addClass("disabled").removeClass("pressed");
            isPlusTwo = false;
        } else {
            $("#input-time").prop("disabled", false).val("");
            $(this).removeClass("pressed");
            $("#btn-plus-two").removeClass("disabled");
        }
    });

    $("#btn-plus-two").click(function() {
        if ($(this).hasClass("disabled")) {
            return;
        }

        isPlusTwo = !isPlusTwo;

        if (isPlusTwo) {
            $(this).addClass("pressed");
        } else {
            $(this).removeClass("pressed");
        }
    });
});