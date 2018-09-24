(function() {
 
    function init() {
        window.app.timer = new window.app.Timer();

        window.app.eventsDataManager = new window.app.EventsDataManager();

        window.app.currentScramblesManager = new window.app.CurrentScramblesManager();

        window.app.solveCardManager = new window.app.SolveCardManager();
        window.app.timerDisplayManager = new window.app.TimerDisplayManager();
        window.app.scrambleDisplayManager = new window.app.ScrambleDisplayManager();
    };

    $(init);
  
})();