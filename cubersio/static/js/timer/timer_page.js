(function(){

    // Timer stuff
    // TODO comment better
    window.app.timer = new window.app.Timer(window.app.eventName);
    window.app.timerDisplayManager = new window.app.TimerDisplayManager();

    if (window.app.isComplete) {
        window.app.timer._reset();
        window.app.timer._disable();
    }

})();