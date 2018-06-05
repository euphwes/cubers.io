var currentTime = 1;
var currentInspectionTime = 15;
var isTimerRunning = false;
var isInspection = false;
var timerIsPlusTwo = false;
var timerIsDNF = false;

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
        isTimerRunning = false;
    }
}

function timerIntervalFunction() {
    currentTime++;

    $timerText.html(convertSecondsToMinutes(currentTime / 100));
}

function startInspection() {
    isPlusTwo = false;
    isDNF = false;
    currentTime = 55.00;
    isTimerRunning = true;
    isInspection = true;
    $timerText.html(currentInspectionTime);
    inspectionInterval = setInterval(inspectionIntervalFunction, 1000);
}

function stopInspection() {
    clearInterval(inspectionInterval);
    isInspection = false;
    currentInspectionTime = 15;
}

function startTimer() {
    timerInterval = setInterval(timerIntervalFunction, 10);
}

function stopTimer() {
    isTimerRunning = false;
    clearInterval(timerInterval);
}

function onTimerActionKey() {
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