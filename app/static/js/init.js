(function() {
    var app = window.app;
 
    /**
     * Initializes all the modules in the app.
     * 
     * NOTE: many of these constructors below depend on being called in the right order,
     * so that they events they are listening to are already defined in `app`.
     * DON'T CHANGE THIS ORDER (unless you know what you are doing).
     */
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

        app.eventsDataManager.buildAllIncompleteSummaries();
    };

    $(init);
})();