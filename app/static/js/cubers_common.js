var selectedScramble = null;
var selectedEvent = null;
var isDNF = false;
var isPlusTwo = false;

var events = {};

function selectScramble(scramble) {
    if (selectedScramble != null) {
        selectedScramble.$element.removeClass("active");
    }

    if (scramble != null) {
        selectedScramble = scramble
        scramble.$element.addClass("active");

        $("#btn-dnf").removeClass("disabled").addClass("btn-outline-danger").removeClass("btn-danger");
        $("#btn-plus-two").removeClass("disabled").addClass("btn-outline-warning").removeClass("btn-warning");;
        $("#btn-enter-time").removeClass("disabled")
        $("#input-time").attr("placeholder", "Time for Scramble " + scramble.num).attr("aria-label", "Time for Scramble " + scramble.num).prop("disabled", false);
    } else {
        // We've reached the last scramble, or we don't want any selected.
        selectedScramble = null;
        $("#input-time").attr("placeholder", "Please select a scramble").prop("disabled", true);
        $("#btn-enter-time").addClass("disabled");
        $("#btn-dnf").addClass("disabled").addClass("btn-outline-danger").removeClass("btn-danger");
        $("#btn-plus-two").addClass("disabled").addClass("btn-outline-warning").removeClass("btn-warning");
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

function enterTime(scramble, time) {
    if (scramble == null || $("#btn-enter-time").hasClass("disabled")) {
        return;
    }

    scramble.isDNF = isDNF;
    scramble.isPlusTwo = isPlusTwo;

    if (time != "DNF") {
        time = parseFloat(time)

        if (isPlusTwo) {
            time += 2.0;
        }

        time = time.toFixed(3);
        scramble.$element.removeClass("dnf");
    } else {
        scramble.$element.addClass("dnf");
    }

    if (isPlusTwo) {
        scramble.$element.addClass("plus-two");
    } else {
        scramble.$element.removeClass("plus-two");
    }

    scramble.time = time;
    scramble.$element.addClass("solved");
    scramble.$element.find(".scramble-time").html(time);

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

    $("#btn-dnf").click(function() {
        isDNF = !isDNF;

        if (isDNF) {
            $("#input-time").prop("disabled", true).val("DNF");
            $(this).addClass("btn-danger").removeClass("btn-outline-danger");
            $("#btn-plus-two").addClass("disabled").addClass("btn-outline-warning").removeClass("btn-warning");
            isPlusTwo = false;
        } else {
            $("#input-time").prop("disabled", false).val("");
            $(this).addClass("btn-outline-danger").removeClass("btn-danger");
            $("#btn-plus-two").removeClass("disabled");
        }
    });

    $("#btn-plus-two").click(function() {
        if ($(this).hasClass("disabled")) {
            return;
        }

        isPlusTwo = !isPlusTwo;

        if (isPlusTwo) {
            $(this).addClass("btn-warning").removeClass("btn-outline-warning");
        } else {
            $(this).addClass("btn-outline-warning").removeClass("btn-warning");
        }
    })
});