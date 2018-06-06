var timerModifierScramble = null;
var currentTime = 0;
var currentInspectionTime = 15;
var isTimerRunning = false;
var isInspection = false;
var timerIsPlusTwo = false;
var timerIsDNF = false;
var timerIsGracePeriod = false;
var timerInterval;
var inspectionInterval;

var $timerText;

function inspectionIntervalFunction() {
    currentInspectionTime -= 1;

    if (currentInspectionTime > 0) {
        $timerText.html(currentInspectionTime);
    } else if (currentInspectionTime <= 0 && currentInspectionTime > -2) {
        $timerText.html(currentInspectionTime + " +2");
        timerIsPlusTwo = true;
    } else {
        $timerText.html(currentInspectionTime + " DNF");
        timerIsDNF = true;

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
    currentTime = 55.00;
    isTimerRunning = true;
    isInspection = true;
    selectedScramble.isDNF = false;
    selectedScramble.isPlusTwo = false;

    $timerText.html(currentInspectionTime);

    $(".btn-dnf, .btn-plus-two").removeClass("pressed");
    $(".btn-switch-mode, #btn-continue, #timer-event-tabs .event-tab, .btn-scrambles").addClass("disabled");
    setModifierButtonsEnabled(false);

    

    inspectionInterval = setInterval(inspectionIntervalFunction, 1000);
}

function stopInspection() {
    clearInterval(inspectionInterval);
    isInspection = false;
    currentInspectionTime = 15;
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

    timerModifierScramble = selectedScramble;

    currentTime = currentTime / 100;
    enterTime(selectedScramble, currentTime);
    selectScramble(getNextScramble(selectedEvent));

    setModifierButtonsEnabled(true);


    $(".btn-switch-mode, #btn-continue, #timer-event-tabs .event-tab, .btn-scrambles").removeClass("disabled");
}

function setModifierButtonsEnabled(flag) {
    if (flag) {
        selectedEvent.$timer.find(".btn-dnf.timer-btn , .btn-plus-two.timer-btn").removeClass("disabled");
    } else {
        selectedEvent.$timer.find(".btn-dnf.timer-btn , .btn-plus-two.timer-btn").addClass("disabled");
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

$(document).ready(function() {
    $(document).on('keypress', function(e) {
        if (currentMode == 1) { // CurrentMode is defined in cubers_common.js
            if (e.which == 32) {
                    onTimerActionKey();
            } else if (isTimerRunning) {
                onTimerActionKey();
            }
        }
    });

    $("#timer-event-tabs .event-tab").click(function() {
        if (!$(this).hasClass("disabled")) {
            var eventId = $(this).data("competitionEventId");

            onTabSwitch(eventId);
        }
    });

    $("#dv-timer .result").click(function() {
        selectScramble(getScramble($(this).data("scrambleId")));
        timerModifierScramble = selectedScramble;
        setModifierButtonsEnabled(true);
    });

    $(".scrambles-dropdown .dropdown-item").click(function() {
        selectScramble(getScramble($(this).data("scrambleId")));
        timerModifierScramble = selectedScramble;

        if (selectedScramble.time == 0) {
            $timerText.html("ready");
            setModifierButtonsEnabled(false);
        } else {
            setModifierButtonsEnabled(true);
        }
        //$this.parent().siblings(".btn-scrambles").html($this.html());
    });

    $("#btn-submit").click(function() {
        submitResults();
    })
});