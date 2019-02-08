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
        app.is_mobile = Boolean(new MobileDetect(window.navigator.userAgent).mobile());

        app.scramblePreviewUnsupportedEvents = ["2BLD", "3BLD", "4BLD", "5BLD", "COLL",
        "Kilominx", "3x3 Mirror Blocks/Bump", "3x3x4", "3x3x5", "2-3-4 Relay",
        "3x3 Relay of 3", "PLL Time Attack"];

        app.appModeManager = new app.AppModeManager();

        app.userSettingsManager = new app.UserSettingsManager();

        app.timer = new app.Timer();

        app.eventsDataManager = new app.EventsDataManager();
        app.currentScramblesManager = new app.CurrentScramblesManager();

        app.solveCardManager = new app.SolveCardManager();
        app.timerDisplayManager = new app.TimerDisplayManager();
        app.scrambleDisplayManager = new app.ScrambleDisplayManager();
        app.scrambleImageGenerator = new app.ScrambleImageGenerator();

        app.mainScreenManager = new app.MainScreenManager();
        app.timerScreenManager = new app.TimerScreenManager();
        app.summaryScreenManager = new app.SummaryScreenManager();

        app.eventsDataManager.buildAllIncompleteSummaries();

        window.scrollTo(0,1);
    }

    $(init);
})();