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

var events = {};

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
    events[eventId] = { id: eventId, name: eventName, scrambles: [], comment: "" , $timer: $("#timer-" + eventName)};
}

function addScramble(eventId, scrambleId, scrambleValue) {
    events[eventId].scrambles.push({ id: scrambleId, scramble: scrambleValue, time: 0, unmodifiedTime: 0, plusTwo: false, isDNF: false, num: events[eventId].scrambles.length + 1, plusTwoLock: false, dnfLock: false });
}

function convertMinutestoSeconds(timeString) {
    var parts = timeString.split(":");

    if (parts.length <= 1 || parseFloat(parts[1]) >= 60) {
        // If we're in minute format, the seconds can't be over 60 (aka 12 minutes and 76 seconds doesn't make sense)
        return Number.NaN;
    }

    return parseInt(parts[0]) * 60 + parseFloat(parts[1])
}

function convertSecondsToMinutes(time) {
    if (time < 60) {
        return time.toFixed(2);
    } else {
        var mins = Math.floor(time / 60);
        var secs = (time - mins * 60).toFixed(2);

        if (secs.length == 4) {
            secs = "0".concat(secs);
        }

        return mins + ":" + secs;
    }
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
                completedTimes.push(scramble.time.toFixed(2));

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

            average = (average / averageCount).toFixed(2);
        }

        if (average != "DNF" && completedTimes.length >= 5) {
            completedTimes[maxIndex] = "(" + completedTimes[maxIndex] + ")";
            
            if (numDNF == 0) {
                completedTimes[minIndex] = "(" + completedTimes[minIndex] + ")";
            }
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
}

function submitResults() {
    var sanitziedResults = {};

    keys = Object.keys(events);

    for (var i = 0; i < keys.length; i++) {
        var event = events[keys[i]];

        var o = { scrambles: [], comment: "This is a default comment. Wow! Look at that average! Isn't Petrus such a hard method? I should really learn F2L..." }

        for (var j = 0; j < event.scrambles; j++) {
            var scramble = event.scrambles[j];

            o.scrambles.push({ id: scramble.id, time: scramble.time, isPlusTwo: scramble.isPlusTwo, isDNF: scramble.isDNF })
        }

        sanitziedResults[event.id] = o;
    }

    $("#input-results").val(JSON.stringify(sanitziedResults));
    $("#form-results").submit();
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

    $("#btn-continue").click(function() {
        if (!$(this).hasClass("disabled")) {
            $("#card-time-entry").fadeOut(function() {
                $("#card-submit").fadeIn();
            });
            buildOverview();
        }
    });

    $("#btn-submit").click(function() {
        submitResults();
    })

    $("#btn-cancel-submit").click(function() {
        $("#card-submit").fadeOut(function() {
            $("#card-time-entry").fadeIn();
        });
    })
});