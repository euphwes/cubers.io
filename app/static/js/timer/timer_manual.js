(function () {

    function verifyAndProcessManualTime(e) {
        if (e.preventDefault) {
            e.preventDefault();
        }

        /* do what you want with the form */

        // You must return false to prevent the default form behavior
        return false;
    }

    $('#manualEntryForm').submit(verifyAndProcessManualTime);

})();