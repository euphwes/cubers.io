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

    function verifyAndProcessFMCEntry(e, isDNFByButton) {
        var currentValue = $('#manualEntryInput').val();
        var isDNF = isDNFByButton || false;
        var asInt = 99900;

        var showInvalid = function() {
            bootbox.alert('Please use the "solution" button below to enter a solution for this scramble.');
        }

        if (!isDNF) {
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
        solve_data.fmc_comment = window.app.fmc_comment;

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
        var combined_scramble_solution = scramble + ' ' + solution;
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
        if (commentStartIndex > -1) {
            return line.substr(0, commentStartIndex);
        }

        commentStartIndex = line.indexOf("\\");
        if (commentStartIndex > -1) {
            return line.substr(0, commentStartIndex);
        }

        commentStartIndex = line.indexOf("#");
        if (commentStartIndex > -1) {
            return line.substr(0, commentStartIndex);
        }

        commentStartIndex = line.indexOf("-");
        if (commentStartIndex > -1) {
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

        var validMoves = [
            "U", "U2", "U'",
            "F", "F2", "F'",
            "R", "R2", "R'",
            "L", "L2", "L'",
            "D", "D2", "D'",
            "B", "B2", "B'",
            "Uw", "Uw2", "Uw'",
            "Fw", "Fw2", "Fw'",
            "Rw", "Rw2", "Rw'",
            "Lw", "Lw2", "Lw'",
            "Dw", "Dw2", "Dw'",
            "Bw", "Bw2", "Bw'",
            "M", "M2", "M'",
            "S", "S2", "S'",
            "E", "E2", "E'",
            "x", "x2", "x'",
            "y", "y2", "y'",
            "z", "z2", "z'",
        ];

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
                if (!validMoves.includes(chunk)) { return; }

                moves.push(chunk);
            });
        });

        return moves;
    };

    // Gets a move count in Outer Block Turn Metric for a given solution
    function getOBTMMoveCount(moves) {
        var sliceMoves = ["E", "E2", "E'", "M", "M2", "M'", "S", "S2", "S'"];
        var rotations  = ["x", "x2", "x'", "y", "y2", "y'", "z", "z2", "z'"];

        var moveCount = 0;
        $.each(moves, function(i, move) {
            if (sliceMoves.includes(move)) {
                moveCount += 2;
            } else if (rotations.includes(move)) {
                moveCount += 0;
            } else {
                moveCount += 1;
            }
        });

        return moveCount;
    };

    // Normalizes a move sequence by reducing pairs of face turns (e.g. R R --> R2)
    // and removing rotations and adjusting later moves to account for that
    function normalizeMoveSequence(moveSequence) {

        console.log('\nnormalizing: ' + moveSequence);

        // Brute force, expand all variants of x, y, z into repeated rotations
        // x' --> x x x
        // y2 --> y y
        // etc
        //
        // We don't need to worry about rotations outside this hardcoded list, because we
        // filtered those out as invalid moves earlier.
        moveSequence = moveSequence.replace(/x2/g, 'x x');
        moveSequence = moveSequence.replace(/x'/g, 'x x x');
        moveSequence = moveSequence.replace(/y2/g, 'y y');
        moveSequence = moveSequence.replace(/y'/g, 'y y y');
        moveSequence = moveSequence.replace(/z2/g, 'z z');
        moveSequence = moveSequence.replace(/z'/g, 'z z z');

        console.log('expanded rotations: ' + moveSequence);

        var moves = moveSequence.split(/\s+/);

        var rotation_transforms = {
            'x': {
                'U': 'F',
                'B': 'U',
                'D': 'B',
                'F': 'D',
                'L': 'L',
                'R': 'R',
            },
            'y': {
                'L': 'F',
                'B': 'L',
                'R': 'B',
                'F': 'R',
                'U': 'U',
                'D': 'D',
            },
            'z': {
                'R': 'U',
                'D': 'R',
                'L': 'D',
                'U': 'L',
                'F': 'F',
                'B': 'B',
            }
        }

        // Utility function to find the index of the last rotation (x, y, z) in the given
        // move sequence, as well as which rotation it is
        var getIndexOfLastRotationAndRotation = function(sequence) {
            var xLastIndex = sequence.lastIndexOf('x');
            var yLastIndex = sequence.lastIndexOf('y');
            var zLastIndex = sequence.lastIndexOf('z');

            var lastRotationIndex = Math.max(xLastIndex, yLastIndex, zLastIndex);
            if (lastRotationIndex == -1) {
                return [-1, null];
            }

            if (lastRotationIndex == xLastIndex) { return [lastRotationIndex, 'x']; }
            if (lastRotationIndex == yLastIndex) { return [lastRotationIndex, 'y']; }
            if (lastRotationIndex == zLastIndex) { return [lastRotationIndex, 'z']; }
        };

        // While the move sequence still contains a rotation, get the last rotation in the sequence,
        // remove it, and apply the appropriate transformations to the moves that come after it.
        while(true) {
            var lastRotationIndexInfo = getIndexOfLastRotationAndRotation(moves);
            var i = lastRotationIndexInfo[0];
            var whichRotation = lastRotationIndexInfo[1];

            if (i == -1) { break; }

            var transforms_map = rotation_transforms[whichRotation];

            var toBePreserved = moves.slice(0, i);
            var toBeTransformed = moves.slice(i+1, moves.length);
            var transformed = [];

            $.each(toBeTransformed, function(i, move) {
                var face = move[0];
                var targetFace = transforms_map[face];
                transformed.push(move.replace(face, targetFace));
            });

            moves = toBePreserved.concat(transformed);
        }

        console.log('after rotation transforms: ' + moves.join(' '));

        // Returns a 'count' for a given move
        // 1 for single turn clockwise, 2 for double, 3 for single turn counterclockwise
        // Summing these values up and then mod by 4 gives you a single 0-3 value which can be
        // turned back into the simplified move
        var getCountForMove = function(move) {
            return move.includes("'") ? 3
                : move.includes("2") ? 2
                : 1;
        };

        // Returns the simplified move for the given face and the total sum of turns
        // R R R R2 R' R2 --> [R, 10] --> R2
        var getSimplifiedMoveForCount = function(move, count) {
            count = count % 4;
            return count == 1 ? move
                : count == 2 ? move + "2"
                : move + "'";
        };

        var currFace = "";
        var currSum = 0;
        var moveGroups = [];

        // Iterate through the move sequence, grouping runs of similar moves, maintaining a count
        // for each, where count indicates a total number of 90 deg clockwise turns for each
        //
        // R R R2 R' U U' U2 --> [[R, 7], [U, 6]]
        $.each(moves, function(i, move) {
            var face = move[0];

            if (face == currFace) {
                currSum += getCountForMove(move);
            } else {
                if (i > 0) {
                    moveGroups.push([currFace, currSum]);
                }

                currFace = face;
                currSum = getCountForMove(move);
            }
        });
        moveGroups.push([currFace, currSum]);

        // Iterate each group of moves, and push its simplified representation to the
        // simplified move sequence
        //
        // [[R, 7], [U, 6]] --> [R', U2]
        var simplifiedMoveSequence = [];
        $.each(moveGroups, function(i, moveGroup) {
            var simplifiedMove = getSimplifiedMoveForCount(moveGroup[0], moveGroup[1]);
            simplifiedMoveSequence.push(simplifiedMove);
        });

        // Join the simplified move sequence back into a string representation
        return simplifiedMoveSequence.join(' ');
    };

    // Shamelessy adapted from https://codegolf.stackexchange.com/questions/130191/reverse-a-rubiks-cube-algorithm
    // Accepts a move sequence string and returns its inverse.
    function inverseMoveSequence(moveSequence) {
        return moveSequence
            .split(/\s+/)
            .map(([a,b])=>b?+b?a+b:a:a+"'")
            .reverse()
            .join(' ');
    };

    // Wire up the FMC DNF button
    $('#BTN_FMC_DNF').click(function() {
        $('#BTN_FMC_DNF').blur();
        bootbox.confirm({
            message: "Are you sure you want to submit a DNF result?",
            callback: function(result) {
                // Confirm box was closed/canceled, so don't take any action
                if (!result) { return; }

                // Submit results with DNF flag
                verifyAndProcessFMCEntry(null, true);
            }
        });
    });

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

                window.app.fmc_comment = result;

                var raw_solution = sanitizeSolutionAndGetRawMoves(result);
                var solution = raw_solution.join(' ');

                var solution_length = getOBTMMoveCount(raw_solution);
                console.log('parsed solution: ' + solution);
                console.log('calculated OTBM solution length: ' + solution_length);

                var solution_is_valid = doesSolutionSolveScramble(solution, window.app.scramble);

                // inverse the scramble, and compare the solution to that
                var inversed_scramble = inverseMoveSequence(window.app.scramble);
                var solution_is_inverse_scramble = solution == inversed_scramble;

                var normalized_solution = normalizeMoveSequence(solution);
                console.log('normalized solution: ' + normalized_solution);
                var normalized_solution_is_inverse_scramble = normalized_solution == inversed_scramble;

                if (!solution_is_valid) {
                    var msg = "Your solution doesn't appear to solve the provided scramble!<br>";
                    msg += "Please double-check your solution for correctness and typos.<br><br>";
                    msg += "Here is how your solution was interpreted:<br><br>";
                    msg += "<div class=\"code\">" + solution + "</div>";
                    bootbox.alert(msg);
                    return;
                } else if (solution_is_inverse_scramble) {
                    var msg = "Your solution appears to be the inverse of the scramble.<br>";
                    msg += "Please submit your own original solution for this scramble.<br><br>";
                    msg += "Here is how your solution was interpreted:<br><br>";
                    msg += "<div class=\"code\">" + solution + "</div>";
                    bootbox.alert(msg);
                    return;
                } else if (normalized_solution_is_inverse_scramble) {
                    var msg = "Your solution appears to be the inverse of the scramble.<br>";
                    msg += "Please submit your own original solution for this scramble.<br><br>";
                    msg += "Here is how your solution was interpreted:<br><br>";
                    msg += "<div class=\"code\">" + solution + "</div><br>";
                    msg += "Here is your simplified solution, after removing rotations and redundant face turns:<br><br>";
                    msg += "<div class=\"code\">" + normalized_solution + "</div>";
                    bootbox.alert(msg);
                    return;
                } else {
                    $('#manualEntryInput').val(solution_length);
                }
            }
        });
    });

    $('#manualEntryInput').on('keypress', disallowNonDigitsAndDNF);

    $('#manualEntryForm').submit(verifyAndProcessFMCEntry);
    $('#manualEntryInput').focus();
})();