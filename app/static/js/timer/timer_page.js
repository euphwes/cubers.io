(function(){

    // Immediately fit the scramble text to the scramble container, and setup a window resize callback to keep
    // performing that text resize on desktop.
    var fitText = function() { textFit($('.scram')[0], {multiLine: true, maxFontSize: 50}); };
    fitText();
    $(window).resize(fitText);

    new window.app.ScrambleImageGenerator();
})();