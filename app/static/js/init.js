(function() {
 
    function init() {
        window.app.appModeManager = new window.app.AppModeManager();

        window.app.timer = new window.app.Timer();

        window.app.eventsDataManager = new window.app.EventsDataManager();
        window.app.currentScramblesManager = new window.app.CurrentScramblesManager();

        window.app.solveCardManager = new window.app.SolveCardManager();
        window.app.timerDisplayManager = new window.app.TimerDisplayManager();
        window.app.scrambleDisplayManager = new window.app.ScrambleDisplayManager();

        window.app.mainScreenManager = new window.app.MainScreenManager();
        window.app.timerScreenManager = new window.app.TimerScreenManager();
        window.app.summaryScreenManager = new window.app.SummaryScreenManager();
    };

    $(init);
  
})();