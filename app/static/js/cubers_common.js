var timeOverviewTemplate = '<li class="list-group-item list-group-item-action" data-event-id="{0}" style="cursor: pointer;">\
                                <div class="row">\
                                    <div class="col-lg-2 col-md-12">\
                                        <h5 class="mb-1" style="overflow-wrap: normal">{1}</h5>\
                                        <span class="unfinished-warning text-danger" style="text-align: right">Unfinished</span>\
                                    </div>\
                                    <div class="col-lg-3 col-md-12"><strong style="text-align: center">Average: {2}</strong></div>\
                                    <div class="col-lg-7 col-md-12"><p class="mb-1" style="text-align: center">{3}</p></div>\
                                </div>\
                            </li>'

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
        var event = events[keys[i]];

        for (var j = 0; j < event.scrambles.length; j++) {
            scramble = event.scrambles[j];

            if (scramble.id == scrambleId) {
                return scramble;
            }
        }
    }

    return null;
}

function getNextScramble(event) {
    for (var i = 0; i < event.scrambles.length; i++) {
        var scramble = event.scrambles[i];

        if (scramble.time == 0) {
            return scramble;
        }
    }

    return null;
}

function addEvent(eventId, eventName) {
    events[eventId] = { id: eventId, name: eventName, scrambles: [], comment: "" };
}

function addScramble(eventId, scrambleId) {
    events[eventId].scrambles.push({ id: scrambleId, time: 0, plusTwo: false, isDNF: false, num: events[eventId].scrambles.length + 1, $element: $(".scrambles .scramble[data-scramble-id=" + scrambleId + "]")});
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
        scramble.time = time;
    } else {
        scramble.$element.addClass("dnf");
        scramble.$element.find(".scramble-time").html("DNF");
        scramble.time = -1;
    }

    if (isPlusTwo) {
        scramble.$element.addClass("plus-two");
    } else {
        scramble.$element.removeClass("plus-two");
    }

    scramble.$element.addClass("solved");

    selectScramble(getNextScramble(selectedEvent));
    $("#input-time").val("");
}

function buildOverview() {
    $("#overview").empty();

    keys = Object.keys(events);

    var unfinishedCount = 0;

    for (var i = 0; i < keys.length; i++) {
        var event = events[keys[i]];
        var completedTimes = [];
        var average = 0;
        var averageCount = 0;
        var maxIndex = 0;
        var minIndex = 0;
        var numDNF = 0;

        // This loop does four things in one: It serves as a way to check if all the scrambles have been solved (if completedTimes.length == scrambles.length).
        // It also finds the min and max times to not include them in the average by checking as it goes along.
        // It also calculates the average (once the min and max are taken out, if it's an Ao5)
        // Finally, it counts DNF's and makes sure that the average adjusts accordingly
        for (var j = 0; j < event.scrambles.length; j++) {
            var scramble = event.scrambles[j];

            if (scramble.time != 0) {
                completedTimes.push(scramble.time.toFixed(3));

                if (scramble.isDNF === false) {
                    average += scramble.time;
                    averageCount++;
                    
                    if (scramble.time > completedTimes[maxIndex]) {
                        maxIndex = completedTimes.length - 1;
                    } else if (scramble.time < completedTimes[minIndex]) {
                        minIndex = completedTimes.length - 1;
                    }
                } else {
                    numDNF++;
                }
            }
        }

        for (var j = 0; j < completedTimes.length; j++) {
            if (parseFloat(completedTimes[j]) == -1) {
                completedTimes[j] = "DNF";
            }
        }

        // Works out whether the average needs to be DNF or needs to have any times subtracted if there are >= 5 solves
        if (numDNF > 1) {
            average = "DNF";
        } else if (completedTimes.length < 5 && numDNF > 0) {
            average = "DNF"
        } else {
            if (completedTimes.length >= 5) {
                // Cancel out the best and worst
                if (numDNF == 0) {
                    average -= parseFloat(completedTimes[maxIndex]) + parseFloat(completedTimes[minIndex]);
                    averageCount -= 2;
                } else {
                    average -= completedTimes[maxIndex];
                    averageCount -= 1;
                }
            }

            average = (average / averageCount).toFixed(3);
        }

        if (completedTimes.length >= 5) {
            completedTimes[maxIndex] = "(" + completedTimes[maxIndex] + ")";
            completedTimes[minIndex] = "(" + completedTimes[minIndex] + ")";
        }

        if (completedTimes.length > 0) {
            var $item = $(timeOverviewTemplate.format(event.id, event.name, average, completedTimes.join(", "))).appendTo($("#overview"));
            
            if (completedTimes.length != event.scrambles.length) {
                $item.addClass("unfinished");
                unfinishedCount++;
            }

            $item.click(function() {

                var eventId = $(this).data("eventId")

                //$("#event-tabs .event-tab.active").removeClass(".active");
                $("#event-tabs .event-tab[data-competition-event-id=" + eventId + "]").click();

                //onTabSwitch(eventId);

                $("#card-submit").fadeOut(function() {
                    $("#card-time-entry").fadeIn();
                });
            });
        }
    }

    if (unfinishedCount > 0) {
        $("#unfinished-events-warning").show();
    } else {
        $("#unfinished-events-warning").hide();
    }

    $("#card-time-entry").fadeOut(function() {
        $("#card-submit").fadeIn();
    });
}

$(document).ready(function() {
    // template.format(param1, param2, param3) (template is type string)
    if (!String.prototype.format) {
        String.prototype.format = function() {
            var args = arguments;
            return this.replace(/{(\d+)}/g, function(match, number) { 
                return typeof args[number] != 'undefined'
                    ? args[number]
                    : match
                ;
            });
        };
    }

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
        // First is whether it is keys 0-9. 8 and 46 are backspace and delete.
        if (e.which == 13) { // Enter key
            enterTime(selectedScramble, $("#input-time").val());
        } else if (!((e.which >= 48 && e.which <= 57) || (String.fromCharCode(e.which) == ".") || (String.fromCharCode(e.which) == ":") || (e.which == 8) | (e.which == 46))) {
            e.preventDefault();
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

    $("#btn-continue").click(buildOverview);

    $("#btn-cancel-submit").click(function() {
        $("#card-submit").fadeOut(function() {
            $("#card-time-entry").fadeIn();
        });
    })
});