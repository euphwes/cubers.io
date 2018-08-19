var currentTime = 0;
var currentInspectionTime = 1;
var isTimerRunning = false;
var isInspection = false;
var timerIsPlusTwo = false;
var timerIsDNF = false;
var timerIsGracePeriod = false;
var timerInterval;
var inspectionInterval;

var selectedScramble = null;
var selectedEvent = null;
var modifierScramble = null; // The last completed scramble for the +2 and DNF buttons

var $timerText = null;

function selectEvent(eventId) {
    selectedEvent = events[eventId];
    $timerText = selectedEvent.$timer.find(".timer-time");
}
/*
function selectScramble(scramble, isUserSelect) {
    $(".result.active").removeClass("active");

    if (!isUserSelect) {
        modifierScramble = selectedScramble;
        selectedScramble = scramble;

        if (scramble != null) {
            if (!modifierScramble.timerLock) {
                $(".btn-dnf").prop("disabled", false).removeClass("pressed");
                $(".btn-plus-two").prop("disabled", false).removeClass("pressed");
            } else {
                $(".btn-dnf").prop("disabled", true).removeClass("pressed");
                $(".btn-plus-two").prop("disabled", true).removeClass("pressed");
            }
            
            selectedEvent.$timer.find(".btn-scrambles").html(scramble.num + ". " + scramble.scramble);

            if (modifierScramble.time != 0) {
                if (!modifierScramble.isDNF) {
                    $timerText.html(convertSecondsToMinutes(scramble.time));
                } else {
                    $timerText.html("DNF");
                }
                
                $("#timer-result-" + scramble.id).addClass("active");
            }

            if (scramble.unmodifiedTime != 0) {
                if (scramble.timerLock) {
                    setModifierButtonsEnabled(false);
                } else {
                    setModifierButtonsEnabled(true);
                }

                if (scramble.isPlusTwo) {
                    $(".btn-plus-two.timer-btn").addClass("pressed");
                }
            } else if (scramble.isDNF) {
                $(".btn-dnf.timer-btn").addClass("pressed");
            }else if (scramble.time == 0 && modifierScramble == scramble) {
                setModifierButtonsEnabled(false);
            }
        } else {
            $(".btn-dnf").addClass("disabled").removeClass("pressed");
            $(".btn-plus-two").addClass("disabled").removeClass("pressed");

            $timerText.html("done");
        }
    }
}
*/
function inspectionIntervalFunction() {
    currentInspectionTime -= 1;

    if (currentInspectionTime > 0) {
        $timerText.html(currentInspectionTime);
    } else if (currentInspectionTime <= 0 && currentInspectionTime > -2) {
        $timerText.html(currentInspectionTime);
        $(".btn-plus-two").addClass("pressed");
        timerIsPlusTwo = true;
        selectedScramble.plusTwoLock = true;

    } else {
        $timerText.html(currentInspectionTime + " DNF");
        $("btn-plus-two").removeClass("pressed");
        $(".btn-dnf").addClass("pressed");
        timerIsDNF = true;
        timerIsPlusTwo = false;
        selectedScramble.plusTwoLock = false;
        selectedScramble.dnfLock = true;

        stopInspection();
        stopTimer();
        isTimerRunning = false;
    }
}

function timerIntervalFunction() {
    currentTime++;

    $timerText.html(convertSecondsToMinutes(currentTime / 100));
}

function startInspection() {
    timerIsDNF = false;
    timerIsPlusTwo = false;
    currentTime = 0;
    isTimerRunning = true;
    isInspection = true;
    selectedScramble.isDNF = false;
    selectedScramble.isPlusTwo = false;
    selectedScramble.plusTwoLock = false;
    selectedScramble.dnfLock = false;

    $timerText.html(currentInspectionTime);

    $(".btn-dnf, .btn-plus-two").removeClass("pressed");
    $(".btn-switch-mode, #btn-continue, #timer-event-tabs .event-tab, .btn-scrambles").addClass("disabled");
    setModifierButtonsEnabled(false);

    inspectionInterval = setInterval(inspectionIntervalFunction, 1000);
}

function stopInspection() {
    clearInterval(inspectionInterval);
    isInspection = false;
    currentInspectionTime = 1;
}

function startTimer() {
    timerInterval = setInterval(timerIntervalFunction, 10); // In milliseconds
}

function stopTimer() {
    timerIsGracePeriod = true;
    isTimerRunning = false;
    
    // Start 1.5 second grace period so people don't accidentally start again
    setTimeout(function() {
        timerIsGracePeriod = false;
    }, 1500);

    clearInterval(timerInterval);

    selectedScramble.isDNF = timerIsDNF;
    selectedScramble.isPlusTwo = timerIsPlusTwo;

    currentTime = currentTime / 100;

    enterTime(currentTime);

    selectScramble(getNextScramble(selectedEvent), false);

    $(".btn-switch-mode, #btn-continue, #timer-event-tabs .event-tab, .btn-scrambles").removeClass("disabled");
}

function enterTime(time) {
    var scramble = selectedScramble;

    if (!timerIsDNF) {
        scramble.unmodifiedTime = time;
        scramble.time = time;

        if (timerIsPlusTwo) {
            scramble.time += 2.0;
        }

        $("#timer-result-" + scramble.id.toString() + " .value-holder").html(convertSecondsToMinutes(scramble.time));
    } else {
        scramble.time = -1;
        
        $("#timer-result-" + scramble.id.toString() + " .value-holder").html("DNF");
    }
    
    $("#timer-result-" + scramble.id.toString()).addClass("solved");
}

function selectScramble(scramble, isUserSelect) {
    if (scramble != null) {
        selectedEvent.$timer.find(".result.active").removeClass("active");
        setModifierButtonsEnabled(true);

        //debugger;
        if (isUserSelect) {
            selectedScramble = scramble;
            modifierScramble = scramble;

            $(".btn-plus-two, .btn-dnf").removeClass("pressed");
            
            $("#timer-result-" + scramble.id).addClass("active");

            if (scramble.dnfLock) {
                $(".btn-dnf").addClass("disabled");
                $(".btn-plus-two").addClass("disabled");
            } else if (scramble.plusTwoLock) {
                $(".btn-plus-two").addClass("disabled");
            }

            if (scramble.isDNF) {
                $timerText.html("DNF");
                $(".btn-dnf").addClass("pressed");
            } else if (scramble.unmodifiedTime != 0) {
                $timerText.html(convertSecondsToMinutes(scramble.time));

                if (scramble.isPlusTwo) {
                    $(".btn-plus-two").addClass("pressed");
                }
            } else {
                $timerText.html("ready");
                setModifierButtonsEnabled(false);
            }
        } else {
            modifierScramble = selectedScramble;
            selectedScramble = scramble;

            if (modifierScramble.dnfLock) {
                $(".btn-dnf").addClass("disabled");
                $(".btn-plus-two").addClass("disabled");
            } else if (modifierScramble.plusTwoLock) {
                $(".btn-plus-two").addClass("disabled");
            }

            if (modifierScramble.unmodifiedTime != 0) {
                $timerText.html(convertSecondsToMinutes(modifierScramble.time));
            } else if (modifierScramble.isDNF) {
                $timerText.html("DNF");
            }
        }

        selectedEvent.$timer.find(".btn-scrambles").html(selectedScramble.num + ". " + selectedScramble.scramble);
    } else {
        $(".btn-dnf").addClass("disabled").removeClass("pressed");
        $(".btn-plus-two").addClass("disabled").removeClass("pressed");

        $timerText.html("done");
    }
}

function onTimerActionKey() {
    if (selectedScramble == null || timerIsGracePeriod) {
        return;
    }

    if (!isTimerRunning && !isInspection) {
        startInspection();
    } else if (isTimerRunning) {
        if (isInspection) {
            stopInspection();
            startTimer();
        } else {
            stopTimer();
        }
    }
}

function setModifierButtonsEnabled(flag) {
    if (flag) {
        selectedEvent.$timer.find(".btn-dnf.timer-btn , .btn-plus-two.timer-btn").removeClass("disabled");
    } else {
        selectedEvent.$timer.find(".btn-dnf.timer-btn , .btn-plus-two.timer-btn").addClass("disabled");
    }
}

$(document).ready(function() {
    $(document).on('keypress', function(e) {
        if (e.which == 32) {
                onTimerActionKey();
        } else if (isTimerRunning) {
            onTimerActionKey();
        }
    });

    selectEvent(Object.keys(events)[0]);
    selectScramble(getNextScramble(selectedEvent), true);

    $("#timer-event-tabs .event-tab").click(function() {
        if (!$(this).hasClass("disabled")) {
            var eventId = $(this).data("competitionEventId");

            //onTabSwitch(eventId);
        }
    });

    $("#dv-timer .result").click(function() {
        selectedScramble = getScramble($(this).data("scrambleId"));
        modifierScramble = selectedScramble;
        selectScramble(selectedScramble, true);
    });

    $("#dv-timer .btn-dnf").click(function() {
        if ($(this).hasClass("disabled")) {
            return false;
        }

        modifierScramble.isDNF = !modifierScramble.isDNF;

        if (modifierScramble.isDNF) {
            modifierScramble.isPlusTwo = false;
            modifierScramble.time = -1;

            $(".btn-dnf").addClass("pressed");
            $(".btn-plus-two").removeClass("pressed");
            $timerText.html("DNF");
            $("#timer-result-" + modifierScramble.id.toString() + " .value-holder").html("DNF");
        } else {
            if (!modifierScramble.plusTwoLock) {
                modifierScramble.time = modifierScramble.unmodifiedTime;
            } else {
                modifierScramble.time = modifierScramble.unmodifiedTime + 2;
                modifierScramble.isPlusTwo = true;
                $(".btn-plus-two").addClass("pressed");
            }

            $(".btn-dnf").removeClass("pressed");
            $timerText.html(convertSecondsToMinutes(modifierScramble.time));
            $("#timer-result-" + modifierScramble.id.toString() + " .value-holder").html(convertSecondsToMinutes(modifierScramble.time));
        }
    });

    $("#dv-timer .btn-plus-two").click(function() {
        if ($(this).hasClass("disabled")) {
            return false;
        }

        modifierScramble.isPlusTwo = !modifierScramble.isPlusTwo;

        if (modifierScramble.isPlusTwo) {
            modifierScramble.isDNF = false;
            modifierScramble.time = modifierScramble.unmodifiedTime + 2;

            $(".btn-plus-two").addClass("pressed");
            $(".btn-dnf").removeClass("pressed");
        } else {
            modifierScramble.time = modifierScramble.unmodifiedTime;

            $(".btn-plus-two").removeClass("pressed");
        }

        $timerText.html(convertSecondsToMinutes(modifierScramble.time));
        $("#timer-result-" + modifierScramble.id.toString() + " .value-holder").html(convertSecondsToMinutes(modifierScramble.time));
    });

    $(".scrambles-dropdown .dropdown-item").click(function() {
        selectScramble(getScramble($(this).data("scrambleId")), true);
        modifierScramble = selectedScramble;

        if (selectedScramble.time == 0) {
            $timerText.html("ready");
            setModifierButtonsEnabled(false);
        } else {
            setModifierButtonsEnabled(true);
        }
        //$this.parent().siblings(".btn-scrambles").html($this.html());
    });

    $("html, body").click(function() {
        if (isTimerRunning) {
            onTimerActionKey();
        }
    });

    $(".timer-start-zone").click(function(e) {
        onTimerActionKey();
        e.stopPropagation();
    });

    $("#btn-submit").click(function() {
        submitResults();
    })
});