(function() {
    $('.event-card').click(function(e) {
        var $event = $(e.target).closest('.event-card');
        window.location.href = $event.data('compete_url');
        e.preventDefault();
    }.bind(this));
})();