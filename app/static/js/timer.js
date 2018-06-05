var currentTime = 0.000;
var currentInspectionTime = 16;
var isTimerRunning = false;
var isInspection = false;
var timerIsPlusTwo = false;
var timerIsDNF = false;

var timerInterval;
var inspectionInterval;

var $timerText;

function inspectionInterval() {
    currentInspectionTime -= 1;

    if (currentInspectionTime > 0) {
        $timerText.html(currentInspectionTime);
    } else if (currentInspectionTime <= 0 && currentInspectionTime > -2) {
        $timerText.html(currentInspectionTime + " +2");
    } else {
        $timerText.html(currentInspectionTime + " DNF");

        stopInspection();
        isTimerRunning = false;
    }
}

function startInspection() {
    isTimerRunning = true;
    isInspection = true;
    inspectionInterval = setInterval(inspectionInterval, 1000);
}

function stopInspection() {
    clearInterval(inspectionInterval);
    isInspection = false;
    currentInspectionTime = 16;
}

function onTimerActionKey() {
    if (!isTimerRunning && !isInspection) {
        startInspection();
    }
}

$(document).ready(function() {
    $timerText = $("#dv-timer .timer-time");

    $(document).on('keypress', function(e) {
        console.log("Hello");
        if (e.which == 32) {
            // CurrentMode is defined in cubers_common.js
            if (currentMode == 1) {
                onTimerActionKey();
            }
        }
    });
});