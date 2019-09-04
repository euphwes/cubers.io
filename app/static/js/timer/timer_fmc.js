(function () {

    // TODO: comment me plz

    function disallowNonDigitsAndDNF(event) {
        var regex = new RegExp("^[0-9DNFdnf]+$");

        var rawCode = !event.charCode ? event.which : event.charCode;
        if (rawCode == 13) { return true; }

        var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
        if (!regex.test(key)) {
           event.preventDefault();
           return false;
        }
    };

    function verifyAndProcessFMCEntry() {
        var currentValue = $('#manualEntryInput').val();
        var isDNF = false;
        var asInt = 99900;

        var showInvalid = function() {;
            bootbox.alert('"' + currentValue + '" is not a valid result!<br>Please enter "DNF" or number of moves.');
        }

        if (currentValue.toUpperCase() == 'DNF') {
            isDNF = true;
        } else {
            if (currentValue.includes('.') || currentValue.includes(':')) {
                showInvalid();
                return false;
            }
            try {
                asInt = parseInt(currentValue) * 100;
                if (isNaN(asInt)) {
                    showInvalid();
                    return false;
                }
            } catch (error) {
                showInvalid();
                return false;
            }
        }

        var solve_data = {};
        solve_data.scramble_id = window.app.scrambleId;
        solve_data.comp_event_id = window.app.compEventId;
        solve_data.is_dnf = isDNF;
        solve_data.is_plus_two = false;

        if (solve_data.is_dnf) {
            solve_data.elapsed_centiseconds = 99900;
        } else {
            solve_data.elapsed_centiseconds = asInt;
        }

        $.ajax({
            url: '/post_solve',
            type: "POST",
            data: JSON.stringify(solve_data),
            contentType: "application/json",
            success: window.app.reRenderTimer,
            error: function (xhr) {
                bootbox.alert("Something unexpected happened: " + xhr.responseText);
            }
        });

        return false;
    };

    // Determine if a given solution solves a given scramble
    function doesSolutionSolveScramble(solution, scramble) {
        var combined_scramble_solution = solution + ' ' + scramble;
        var state_post_solution = (new window.app.ScrambleImageGenerator()).getCubeState(combined_scramble_solution);

        var solved_states = (new window.app.ScrambleImageGenerator()).getAllSolvedCubeStates();
        var solution_is_valid = false;
        $.each(solved_states, function(i, solved_state) {
            if (state_post_solution == solved_state) {
                solution_is_valid = true;
            }
        });

        return solution_is_valid;
    };

    // Strips comments from solution lines, for common comment formats
    // Examples:
    //       R2 F2 L' D'  // does a thing
    //       R2 F2 L' D'  \\ does a thing
    //       R2 F2 L' D'  # does a thing
    //       R2 F2 L' D'  - does a thing
    function stripComments(line) {
        var commentStartIndex = -1;

        commentStartIndex = line.indexOf("/");
        if (commentStartIndex > 0) {
            return line.substr(0, commentStartIndex);
        }

        commentStartIndex = line.indexOf("\\");
        if (commentStartIndex > 0) {
            return line.substr(0, commentStartIndex);
        }

        commentStartIndex = line.indexOf("#");
        if (commentStartIndex > 0) {
            return line.substr(0, commentStartIndex);
        }

        commentStartIndex = line.indexOf("-");
        if (commentStartIndex > 0) {
            return line.substr(0, commentStartIndex);
        }

        return line;
    };

    // Ensures the solution is written with the casing that the scramble preview generator expects
    function ensureCorrectCasing(line) {
        // face moves and slices should be capitals
        line = line.replace(/r/g, "R");
        line = line.replace(/f/g, "F");
        line = line.replace(/l/g, "L");
        line = line.replace(/b/g, "B");
        line = line.replace(/u/g, "U");
        line = line.replace(/d/g, "D");
        line = line.replace(/e/g, "E");
        line = line.replace(/s/g, "S");
        line = line.replace(/m/g, "M");

        // rotations should be lowercase
        line = line.replace(/X/g, "x");
        line = line.replace(/Y/g, "y");
        line = line.replace(/Z/g, "z");

        return line;
    };

    // Strip out the comments and characters which aren't a valid solution, ensure correct casing,
    // clean up errant whitespace, and return as the raw solution string
    function sanitizeSolutionAndGetRawMoves(result) {
        var moves = [];

        var lines = result.split(/\r?\n/);
        $.each(lines, function(i, line) {
            line = line.trim();
            line = ensureCorrectCasing(line);
            line = stripComments(line);
            line = line.trim();

            if (line == '') { return; }

            $.each(line.split(" "), function(j, chunk) {
                chunk = chunk.trim();
                if (chunk == '') { return; }

                moves.push(chunk);
            });
        });

        return moves;
    };

    // Wire up the FMC comment button
    $('#BTN_FMC_COMMENT').click(function () {
        $('#BTN_FMC_COMMENT').blur();

        bootbox.prompt({
            title: 'Solution',
            value: window.app.fmc_comment,
            inputType: "textarea",
            centerVertical: true,
            buttons: {
                confirm: {
                    label: 'Confirm solution',
                    // className: 'btn-success'
                },
                cancel: {
                    label: 'Cancel',
                    // className: 'btn-danger'
                }
            },
            callback: function (result) {
                // Dialog box was closed/canceled, so don't update comment
                if (result == null) {
                    return;
                }

                var raw_solution = sanitizeSolutionAndGetRawMoves(result);
                var solution = raw_solution.join(' ');

                var solution_is_valid = doesSolutionSolveScramble(solution, window.app.scramble);
                alert(solution_is_valid);

                // validate solution is proper notation
                // validate solution solves cube
                    // yes? get solution length
                    // no? 
            }
        });
    });

    $('#manualEntryInput').on('keypress', disallowNonDigitsAndDNF);

    $('#manualEntryForm').submit(verifyAndProcessFMCEntry);
    $('#manualEntryInput').focus();
})();