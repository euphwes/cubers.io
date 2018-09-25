(function() {
    var app = window.app;

    function SummaryScreenManager() {
        this.summaryPanelTemplate = Handlebars.compile($('#summary-template').html());
    };

    app.SummaryScreenManager = SummaryScreenManager;
})();