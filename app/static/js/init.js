(function() {
    var app = window.app;
 
    function init() {
        app.appModeManager = new app.AppModeManager();

        app.timer = new app.Timer();

        app.eventsDataManager = new app.EventsDataManager();
        app.currentScramblesManager = new app.CurrentScramblesManager();

        app.solveCardManager = new app.SolveCardManager();
        app.timerDisplayManager = new app.TimerDisplayManager();
        app.scrambleDisplayManager = new app.ScrambleDisplayManager();

        app.mainScreenManager = new app.MainScreenManager();
        app.timerScreenManager = new app.TimerScreenManager();
        app.summaryScreenManager = new app.SummaryScreenManager();

        app.eventsDataManager.updateEventsDataCompleteness();
    };

    $(init);
  
})();