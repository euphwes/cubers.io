(function(){

    // Immediately fit the scramble text to the scramble container, and setup a window resize callback to keep
    // performing that text resize on desktop.
    var fitText = function() { textFit($('.scram')[0], {multiLine: true, maxFontSize: 50}); };
    fitText();
    $(window).resize(fitText);

    // Initialize the scramble image generator, which will render the small-size scramble preview
    // Add a click/press handler on the preview to show the large scramble preview
    var imageGenerator = new window.app.ScrambleImageGenerator();
    $('.scramble_preview').click(function(){
        imageGenerator.showLargeImage();
        $('#fade-wrapper').fadeIn().addClass('shown');
        $('#fade-wrapper').click(function(){
            $(this).fadeOut(function(){
                $(this).removeClass('shown');
            });
        });
    });
})();