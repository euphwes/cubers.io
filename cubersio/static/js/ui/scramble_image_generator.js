(function() {
    var app = window.app;

    // Order is         D,      L,      B,      U,      R,      F
    var default_cube_colors = ['#ff0', '#fa0', '#00f', '#fff', '#f00', '#0d0'];
    var cube_colors = ['#ff0', '#fa0', '#00f', '#fff', '#f00', '#0d0'];

    // Order is          U,      B,      R,      D,      F       L
    var skewb_colors = ['#fff', '#00f', '#f00', '#ff0', '#0f0', '#f80'];
    var default_rex_colors   = ['#fff', '#00f', '#f00', '#ff0', '#0f0', '#f80'];
    var rex_colors   = ['#fff', '#00f', '#f00', '#ff0', '#0f0', '#f80'];

    var default_sq1_colors = {
        'U': '#333333',
        'D': '#FFFFFF',
        'L': '#FF8800',
        'F': '#0000FF',
        'R': '#FF0000',
        'B': '#00FF00',
    };
    var sq1_colors = {
        'U': '#333333',
        'D': '#FFFFFF',
        'L': '#FF8800',
        'F': '#0000FF',
        'R': '#FF0000',
        'B': '#00FF00',
    };

    // Order is    U       L          F       R       B       BR         D       BL
    var default_fto_colors = ['#fff', '#800080', '#f00', '#0d0', '#00f', '#bebebe', '#ff0', '#fa0'];
    var fto_colors = ['#fff', '#800080', '#f00', '#0d0', '#00f', '#bebebe', '#ff0', '#fa0'];

    // Order is F, L, R, D
    var default_pyra_colors = ['#0f0', '#f00', '#00f', '#ff0'];
    var pyra_colors = ['#0f0', '#f00', '#00f', '#ff0'];

    var default_mega_colors = ['#fff', '#d00', '#060', '#81f', '#fc0', '#00b', '#ffb', '#8df', '#f83', '#7e0', '#f9f', '#999'];
    var mega_colors = ['#fff', '#d00', '#060', '#81f', '#fc0', '#00b', '#ffb', '#8df', '#f83', '#7e0', '#f9f', '#999'];

    var TRANSPARENT = "rgba(255, 255, 255, 0)";

    // "global"-ish variable to hold the border radius for the current event and canvas size
    var eventCornerRadius = 0;

    // Default to no corner radius for events without an override in the map below
    var defaultCornerRadiusOptions = [0, 0];

    // Border radius config options will be differentiated between small and large canvas
    // sizes, because lots tiny polygons with curved borders end up looking weird on small canvas.
    // Value at index 0 is for small canvas, value at index 1 is for big canvas
    var CANVAS_SMALL_RADIUS_IDX = 0;
    var CANVAS_LARGE_RADIUS_IDX = 1;

    var nxnRadius = 8;
    var cuboidRadius = 4;
    var ftoRadius = 8;

    var cornerRadiusMap = {
        "2x2":    [nxnRadius, nxnRadius],
        "3x3":    [nxnRadius, nxnRadius],
        "3x3":    [nxnRadius, nxnRadius],
        "3x3OH":  [nxnRadius, nxnRadius],
        "2GEN":   [nxnRadius, nxnRadius],
        "LSE":    [nxnRadius, nxnRadius],
        "F2L":    [nxnRadius, nxnRadius],
        "FMC":    [nxnRadius, nxnRadius],
        "COLL":   [nxnRadius, nxnRadius],
        "4x4":    [nxnRadius, nxnRadius],
        "4x4 OH": [nxnRadius, nxnRadius],
        "15 Puzzle": [nxnRadius, nxnRadius],
        "Void Cube":     [nxnRadius, nxnRadius],
        "3x3 With Feet": [nxnRadius, nxnRadius],

        // curved corners on large NxN don't look great in small canvas
        "5x5":    [0, nxnRadius],
        "6x6":    [0, nxnRadius],
        "7x7":    [0, nxnRadius],
        "8x8":    [0, nxnRadius],
        "9x9":    [0, nxnRadius],
        "10x10":  [0, nxnRadius],

        "2x2x3": [cuboidRadius, cuboidRadius],
        "3x3x2": [cuboidRadius, cuboidRadius],
        "3x3x4": [cuboidRadius, cuboidRadius],

        "Pyraminx": [8, 8],
        "Skewb":    [5, 5],

        "Megaminx": [5, 5],
        "Kilominx": [8, 8],

        "Redi Cube": [5, 5],
        "Dino Cube": [12, 12],

        "FTO": [ftoRadius, ftoRadius],
    }

    var setColors = function() {
        if (window.app.userSettingsManager.get_setting(app.Settings.USE_CUSTOM_CUBE_COLORS)) {
            cube_colors = [
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_CUBE_COLOR_D),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_CUBE_COLOR_L),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_CUBE_COLOR_B),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_CUBE_COLOR_U),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_CUBE_COLOR_R),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_CUBE_COLOR_F)
            ];
            skewb_colors = [
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_CUBE_COLOR_U),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_CUBE_COLOR_B),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_CUBE_COLOR_R),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_CUBE_COLOR_D),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_CUBE_COLOR_F),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_CUBE_COLOR_L)
            ];
        }

        if (window.app.userSettingsManager.get_setting(app.Settings.USE_CUSTOM_REX_COLORS)) {
            rex_colors = [
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_REX_COLOR_U),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_REX_COLOR_B),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_REX_COLOR_R),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_REX_COLOR_D),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_REX_COLOR_F),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_REX_COLOR_L)
            ];
        }

        if (window.app.userSettingsManager.get_setting(app.Settings.USE_CUSTOM_PYRAMINX_COLORS)) {
            pyra_colors = [
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_PYRAMINX_COLOR_F),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_PYRAMINX_COLOR_L),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_PYRAMINX_COLOR_R),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_PYRAMINX_COLOR_D)
            ];
        }

        if (window.app.userSettingsManager.get_setting(app.Settings.USE_CUSTOM_MEGAMINX_COLORS)) {
            mega_colors = [
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_MEGAMINX_COLOR_1),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_MEGAMINX_COLOR_2),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_MEGAMINX_COLOR_3),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_MEGAMINX_COLOR_4),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_MEGAMINX_COLOR_5),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_MEGAMINX_COLOR_6),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_MEGAMINX_COLOR_7),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_MEGAMINX_COLOR_8),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_MEGAMINX_COLOR_9),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_MEGAMINX_COLOR_10),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_MEGAMINX_COLOR_11),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_MEGAMINX_COLOR_12),
            ];
        }

        if (window.app.userSettingsManager.get_setting(app.Settings.USE_CUSTOM_FTO_COLORS)) {
            fto_colors = [
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_FTO_COLOR_U),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_FTO_COLOR_L),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_FTO_COLOR_F),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_FTO_COLOR_R),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_FTO_COLOR_B),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_FTO_COLOR_BR),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_FTO_COLOR_D),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_FTO_COLOR_BL)
            ];
        }

        if (window.app.userSettingsManager.get_setting(app.Settings.USE_CUSTOM_SQUAN_COLORS)) {
            sq1_colors = {
                'U': window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_SQUAN_COLOR_U),
                'R': window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_SQUAN_COLOR_R),
                'F': window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_SQUAN_COLOR_F),
                'D': window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_SQUAN_COLOR_D),
                'L': window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_SQUAN_COLOR_L),
                'B': window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_SQUAN_COLOR_B)
            };
        }
    };

    var mathlib = (function() {
        var DEBUG = false;

        var Cnk = [],
            fact = [1];
        for (var i = 0; i < 32; ++i) {
            Cnk[i] = [];
            for (var j = 0; j < 32; ++j) {
                Cnk[i][j] = 0;
            }
        }
        for (var i = 0; i < 32; ++i) {
            Cnk[i][0] = Cnk[i][i] = 1;
            fact[i + 1] = fact[i] * (i + 1);
            for (var j = 1; j < i; ++j) {
                Cnk[i][j] = Cnk[i - 1][j - 1] + Cnk[i - 1][j];
            }
        }

        function circleOri(arr, a, b, c, d, ori) {
            var temp = arr[a];
            arr[a] = arr[d] ^ ori;
            arr[d] = arr[c] ^ ori;
            arr[c] = arr[b] ^ ori;
            arr[b] = temp ^ ori;
        }

        function circle(arr) {
            var length = arguments.length - 1,
                temp = arr[arguments[length]];
            for (var i = length; i > 1; i--) {
                arr[arguments[i]] = arr[arguments[i - 1]];
            }
            arr[arguments[1]] = temp;
            return circle;
        }

        function getPruning(table, index) {
            return table[index >> 3] >> ((index & 7) << 2) & 15;
        }

        function createMove(moveTable, size, doMove, N_MOVES) {
            N_MOVES = N_MOVES || 6;
            for (var j = 0; j < N_MOVES; j++) {
                moveTable[j] = [];
                for (var i = 0; i < size; i++) {
                    moveTable[j][i] = doMove(i, j);
                }
            }
        }

        function edgeMove(arr, m) {
            if (m == 0) { //F
                circleOri(arr, 0, 7, 8, 4, 1);
            } else if (m == 1) { //R
                circleOri(arr, 3, 6, 11, 7, 0);
            } else if (m == 2) { //U
                circleOri(arr, 0, 1, 2, 3, 0);
            } else if (m == 3) { //B
                circleOri(arr, 2, 5, 10, 6, 1);
            } else if (m == 4) { //L
                circleOri(arr, 1, 4, 9, 5, 0);
            } else if (m == 5) { //D
                circleOri(arr, 11, 10, 9, 8, 0);
            }
        }

        function CubieCube() {
            this.ca = [0, 1, 2, 3, 4, 5, 6, 7];
            this.ea = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22];
        }

        CubieCube.EdgeMult = function(a, b, prod) {
            for (var ed = 0; ed < 12; ed++) {
                prod.ea[ed] = a.ea[b.ea[ed] >> 1] ^ (b.ea[ed] & 1);
            }
        }

        CubieCube.CornMult = function(a, b, prod) {
            for (var corn = 0; corn < 8; corn++) {
                var ori = ((a.ca[b.ca[corn] & 7] >> 3) + (b.ca[corn] >> 3)) % 3;
                prod.ca[corn] = a.ca[b.ca[corn] & 7] & 7 | ori << 3;
            }
        }

        CubieCube.CubeMult = function(a, b, prod) {
            CubieCube.CornMult(a, b, prod);
            CubieCube.EdgeMult(a, b, prod);
        }

        CubieCube.prototype.init = function(ca, ea) {
            this.ca = ca.slice();
            this.ea = ea.slice();
            return this;
        }

        CubieCube.prototype.isEqual = function(c) {
            for (var i = 0; i < 8; i++) {
                if (this.ca[i] != c.ca[i]) {
                    return false;
                }
            }
            for (var i = 0; i < 12; i++) {
                if (this.ea[i] != c.ea[i]) {
                    return false;
                }
            }
            return true;
        }

        var cornerFacelet = [
            [8, 9, 20],
            [6, 18, 38],
            [0, 36, 47],
            [2, 45, 11],
            [29, 26, 15],
            [27, 44, 24],
            [33, 53, 42],
            [35, 17, 51]
        ];
        var edgeFacelet = [
            [5, 10],
            [7, 19],
            [3, 37],
            [1, 46],
            [32, 16],
            [28, 25],
            [30, 43],
            [34, 52],
            [23, 12],
            [21, 41],
            [50, 39],
            [48, 14]
        ];

        CubieCube.prototype.toFaceCube = function(cFacelet, eFacelet) {
            cFacelet = cFacelet || cornerFacelet;
            eFacelet = eFacelet || edgeFacelet;
            var ts = "URFDLB";
            var f = [];
            for (var i = 0; i < 54; i++) {
                f[i] = ts[~~(i / 9)];
            }
            for (var c = 0; c < 8; c++) {
                var j = this.ca[c] & 0x7; // cornercubie with index j is at
                var ori = this.ca[c] >> 3; // Orientation of this cubie
                for (var n = 0; n < 3; n++)
                    f[cFacelet[c][(n + ori) % 3]] = ts[~~(cFacelet[j][n] / 9)];
            }
            for (var e = 0; e < 12; e++) {
                var j = this.ea[e] >> 1; // edgecubie with index j is at edgeposition
                var ori = this.ea[e] & 1; // Orientation of this cubie
                for (var n = 0; n < 2; n++)
                    f[eFacelet[e][(n + ori) % 2]] = ts[~~(eFacelet[j][n] / 9)];
            }
            return f.join("");
        }

        CubieCube.prototype.invFrom = function(cc) {
            for (var edge = 0; edge < 12; edge++) {
                this.ea[cc.ea[edge] >> 1] = edge << 1 | cc.ea[edge] & 1;
            }
            for (var corn = 0; corn < 8; corn++) {
                this.ca[cc.ca[corn] & 0x7] = corn | 0x20 >> (cc.ca[corn] >> 3) & 0x18;
            }
            return this;
        }

        CubieCube.prototype.fromFacelet = function(facelet, cFacelet, eFacelet) {
            cFacelet = cFacelet || cornerFacelet;
            eFacelet = eFacelet || edgeFacelet;
            var count = 0;
            var f = [];
            var centers = facelet[4] + facelet[13] + facelet[22] + facelet[31] + facelet[40] + facelet[49];
            for (var i = 0; i < 54; ++i) {
                f[i] = centers.indexOf(facelet[i]);
                if (f[i] == -1) {
                    return -1;
                }
                count += 1 << (f[i] << 2);
            }
            if (count != 0x999999) {
                return -1;
            }
            var col1, col2, i, j, ori;
            for (i = 0; i < 8; ++i) {
                for (ori = 0; ori < 3; ++ori)
                    if (f[cFacelet[i][ori]] == 0 || f[cFacelet[i][ori]] == 3)
                        break;
                col1 = f[cFacelet[i][(ori + 1) % 3]];
                col2 = f[cFacelet[i][(ori + 2) % 3]];
                for (j = 0; j < 8; ++j) {
                    if (col1 == ~~(cFacelet[j][1] / 9) && col2 == ~~(cFacelet[j][2] / 9)) {
                        this.ca[i] = j | ori % 3 << 3;
                        break;
                    }
                }
            }
            for (i = 0; i < 12; ++i) {
                for (j = 0; j < 12; ++j) {
                    if (f[eFacelet[i][0]] == ~~(eFacelet[j][0] / 9) && f[eFacelet[i][1]] == ~~(eFacelet[j][1] / 9)) {
                        this.ea[i] = j << 1;
                        break;
                    }
                    if (f[eFacelet[i][0]] == ~~(eFacelet[j][1] / 9) && f[eFacelet[i][1]] == ~~(eFacelet[j][0] / 9)) {
                        this.ea[i] = j << 1 | 1;
                        break;
                    }
                }
            }
            return this;
        }

        var moveCube = [];
        for (var i = 0; i < 18; i++) {
            moveCube[i] = new CubieCube()
        }
        moveCube[0].init([3, 0, 1, 2, 4, 5, 6, 7], [6, 0, 2, 4, 8, 10, 12, 14, 16, 18, 20, 22]);
        moveCube[3].init([20, 1, 2, 8, 15, 5, 6, 19], [16, 2, 4, 6, 22, 10, 12, 14, 8, 18, 20, 0]);
        moveCube[6].init([9, 21, 2, 3, 16, 12, 6, 7], [0, 19, 4, 6, 8, 17, 12, 14, 3, 11, 20, 22]);
        moveCube[9].init([0, 1, 2, 3, 5, 6, 7, 4], [0, 2, 4, 6, 10, 12, 14, 8, 16, 18, 20, 22]);
        moveCube[12].init([0, 10, 22, 3, 4, 17, 13, 7], [0, 2, 20, 6, 8, 10, 18, 14, 16, 4, 12, 22]);
        moveCube[15].init([0, 1, 11, 23, 4, 5, 18, 14], [0, 2, 4, 23, 8, 10, 12, 21, 16, 18, 7, 15]);
        for (var a = 0; a < 18; a += 3) {
            for (var p = 0; p < 2; p++) {
                CubieCube.EdgeMult(moveCube[a + p], moveCube[a], moveCube[a + p + 1]);
                CubieCube.CornMult(moveCube[a + p], moveCube[a], moveCube[a + p + 1]);
            }
        }

        CubieCube.moveCube = moveCube;

        CubieCube.prototype.edgeCycles = function() {
            var visited = [];
            var small_cycles = [0, 0, 0];
            var cycles = 0;
            var parity = false;
            for (var x = 0; x < 12; ++x) {
                if (visited[x]) {
                    continue
                }
                var length = -1;
                var flip = false;
                var y = x;
                do {
                    visited[y] = true;
                    ++length;
                    flip ^= this.ea[y] & 1;
                    y = this.ea[y] >> 1;
                } while (y != x);
                cycles += length >> 1;
                if (length & 1) {
                    parity = !parity;
                    ++cycles;
                }
                if (flip) {
                    if (length == 0) {
                        ++small_cycles[0];
                    } else if (length & 1) {
                        small_cycles[2] ^= 1;
                    } else {
                        ++small_cycles[1];
                    }
                }
            }
            small_cycles[1] += small_cycles[2];
            if (small_cycles[0] < small_cycles[1]) {
                cycles += (small_cycles[0] + small_cycles[1]) >> 1;
            } else {
                var flip_cycles = [0, 2, 3, 5, 6, 8, 9];
                cycles += small_cycles[1] + flip_cycles[(small_cycles[0] - small_cycles[1]) >> 1];
            }
            return cycles - parity;
        }

        function createPrun(prun, init, size, maxd, doMove, N_MOVES, N_POWER, N_INV) {
            var isMoveTable = $.isArray(doMove);
            N_MOVES = N_MOVES || 6;
            N_POWER = N_POWER || 3;
            N_INV = N_INV || 256;
            maxd = maxd || 256;
            for (var i = 0, len = (size + 7) >>> 3; i < len; i++) {
                prun[i] = -1;
            }
            prun[init >> 3] ^= 15 << ((init & 7) << 2);
            var val = 0;
            // var t = +new Date;
            for (var l = 0; l <= maxd; l++) {
                var done = 0;
                var inv = l >= N_INV;
                var fill = (l + 1) ^ 15;
                var find = inv ? 0xf : l;
                var check = inv ? l : 0xf;

                out: for (var p = 0; p < size; p++, val >>= 4) {
                    if ((p & 7) == 0) {
                        val = prun[p >> 3];
                        if (!inv && val == -1) {
                            p += 7;
                            continue;
                        }
                    }
                    if ((val & 0xf) != find) {
                        continue;
                    }
                    for (var m = 0; m < N_MOVES; m++) {
                        var q = p;
                        for (var c = 0; c < N_POWER; c++) {
                            q = isMoveTable ? doMove[m][q] : doMove(q, m);
                            if (getPruning(prun, q) != check) {
                                continue;
                            }
                            ++done;
                            if (inv) {
                                prun[p >> 3] ^= fill << ((p & 7) << 2);
                                continue out;
                            }
                            prun[q >> 3] ^= fill << ((q & 7) << 2);
                        }
                    }
                }
                if (done == 0) {
                    break;
                }
                if (DEBUG) {
                    console.log(done);
                }
            }
        }

        //state_params: [[init, doMove, size, [maxd], [N_INV]], [...]...]
        function Solver(N_MOVES, N_POWER, state_params) {
            this.N_STATES = state_params.length;
            this.N_MOVES = N_MOVES;
            this.N_POWER = N_POWER;
            this.state_params = state_params;
            this.inited = false;
        }

        var _ = Solver.prototype;

        _.search = function(state, minl, MAXL) {
            MAXL = (MAXL || 99) + 1;
            if (!this.inited) {
                this.move = [];
                this.prun = [];
                for (var i = 0; i < this.N_STATES; i++) {
                    var state_param = this.state_params[i];
                    var init = state_param[0];
                    var doMove = state_param[1];
                    var size = state_param[2];
                    var maxd = state_param[3];
                    var N_INV = state_param[4];
                    this.move[i] = [];
                    this.prun[i] = [];
                    createMove(this.move[i], size, doMove, this.N_MOVES);
                    createPrun(this.prun[i], init, size, maxd, this.move[i], this.N_MOVES, this.N_POWER, N_INV);
                }
                this.inited = true;
            }
            this.sol = [];
            for (var maxl = minl; maxl < MAXL; maxl++) {
                if (this.idaSearch(state, maxl, -1)) {
                    break;
                }
            }
            return maxl == MAXL ? null : this.sol.reverse();
        }

        _.toStr = function(sol, move_map, power_map) {
            var ret = [];
            for (var i = 0; i < sol.length; i++) {
                ret.push(move_map[sol[i][0]] + power_map[sol[i][1]]);
            }
            return ret.join(' ').replace(/ +/g, ' ');
        }

        _.idaSearch = function(state, maxl, lm) {
            var N_STATES = this.N_STATES;
            for (var i = 0; i < N_STATES; i++) {
                if (getPruning(this.prun[i], state[i]) > maxl) {
                    return false;
                }
            }
            if (maxl == 0) {
                return true;
            }
            for (var move = 0; move < this.N_MOVES; move++) {
                if (move == lm) {
                    continue;
                }
                var cur_state = state.slice();
                for (var power = 0; power < this.N_POWER; power++) {
                    for (var i = 0; i < N_STATES; i++) {
                        cur_state[i] = this.move[i][move][cur_state[i]];
                    }
                    if (this.idaSearch(cur_state, maxl - 1, move)) {
                        this.sol.push([move, power]);
                        return true;
                    }
                }
            }
            return false;
        }

        function rndEl(x) {
            return x[~~(Math.random() * x.length)];
        }

        function rn(n) {
            return ~~(Math.random() * n)
        }

        function rndProb(plist) {
            var cum = 0;
            var curIdx = 0;
            for (var i = 0; i < plist.length; i++) {
                if (plist[i] == 0) {
                    continue;
                }
                if (Math.random() < plist[i] / (cum + plist[i])) {
                    curIdx = i;
                }
                cum += plist[i];
            }
            return curIdx;
        }

        function time2str(unix) {
            if (!unix) {
                return 'N/A';
            }
            var date = new Date(unix * 1000);
            return date.getFullYear() + '-' + ('0' + (date.getMonth() + 1)).slice(-2) + '-' + ('0' + date.getDate()).slice(-2) +
                ' ' + ('0' + date.getHours()).slice(-2) + ':' + ('0' + date.getMinutes()).slice(-2) + ':' + ('0' + date.getSeconds()).slice(-2);
        }

        var timeRe = /^\s*(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)\s*$/
        function str2time(val) {
            var m = timeRe.exec(val);
            if (!m) {
                return null;
            }
            var date = new Date(0);
            date.setFullYear(~~m[1]);
            date.setMonth(~~m[2] - 1);
            date.setDate(~~m[3]);
            date.setHours(~~m[4]);
            date.setMinutes(~~m[5]);
            date.setSeconds(~~m[6]);
            return ~~(date.getTime() / 1000);
        }

        return {
            Cnk: Cnk,
            fact: fact,
            getPruning: getPruning,
            createMove: createMove,
            edgeMove: edgeMove,
            circle: circle,
            circleOri: circleOri,
            createPrun: createPrun,
            CubieCube: CubieCube,
            SOLVED_FACELET: "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB",
            rn: rn,
            rndEl: rndEl,
            rndProb: rndProb,
            time2str: time2str,
            str2time: str2time,
            Solver: Solver
        }
    })();

    var clock = (function(rn, Cnk) {
        var moveArr = [
            [0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], //UR
            [0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0], //DR
            [0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0], //DL
            [1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], //UL
            [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], //U
            [0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0], //R
            [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0], //D
            [1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0], //L
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0], //ALL
            [11, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0], //UR
            [0, 0, 0, 0, 0, 0, 11, 0, 0, 0, 0, 1, 1, 1], //DR
            [0, 0, 0, 0, 0, 0, 0, 0, 11, 0, 1, 1, 0, 1], //DL
            [0, 0, 11, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0], //UL
            [11, 0, 11, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0], //U
            [11, 0, 0, 0, 0, 0, 11, 0, 0, 1, 0, 1, 1, 1], //R
            [0, 0, 0, 0, 0, 0, 11, 0, 11, 0, 1, 1, 1, 1], //D
            [0, 0, 11, 0, 0, 0, 0, 0, 11, 1, 1, 1, 0, 1], //L
            [11, 0, 11, 0, 0, 0, 11, 0, 11, 1, 1, 1, 1, 1] //ALL
        ];

        function select(n, k, idx) {
            var r = k;
            var val = 0;
            for (var i = n - 1; i >= 0; i--) {
                if (idx >= Cnk[i][r]) {
                    idx -= Cnk[i][r--];
                    val |= 1 << i;
                }
            }
            return val;
        }

        //invert table 0  1  2  3  4  5  6  7  8  9 10 11
        var invert = [-1, 1, -1, -1, -1, 5, -1, 7, -1, -1, -1, 11];

        function randomState() {
            var ret = [];
            for (var i = 0; i < 14; i++) {
                ret[i] = rn(12);
            }
            return ret;
        }

        /**
         *	@return the length of the solution (the number of non-zero elements in the solution array)
         *		-1: invalid input
         */
        function Solution(clock, solution) {
            if (clock.length != 14 || solution.length != 18) {
                return -1;
            }
            return solveIn(14, clock, solution);
        }

        function swap(arr, row1, row2) {
            var tmp = arr[row1];
            arr[row1] = arr[row2];
            arr[row2] = tmp;
        }

        function addTo(arr, row1, row2, startidx, mul) {
            var length = arr[0].length;
            for (var i = startidx; i < length; i++) {
                arr[row2][i] = (arr[row2][i] + arr[row1][i] * mul) % 12;
            }
        }

        //linearly dependent
        var ld_list = [7695, 42588, 47187, 85158, 86697, 156568, 181700, 209201, 231778];

        function solveIn(k, numbers, solution) {
            var n = 18;
            var min_nz = k + 1;

            for (var idx = 0; idx < Cnk[n][k]; idx++) {
                var val = select(n, k, idx);
                var isLD = false;
                for (var r = 0; r < ld_list.length; r++) {
                    if ((val & ld_list[r]) == ld_list[r]) {
                        isLD = true;
                        break;
                    }
                }
                if (isLD) {
                    continue;
                }
                var map = [];
                var cnt = 0;
                for (var j = 0; j < n; j++) {
                    if (((val >> j) & 1) == 1) {
                        map[cnt++] = j;
                    }
                }
                var arr = [];
                for (var i = 0; i < 14; i++) {
                    arr[i] = [];
                    for (var j = 0; j < k; j++) {
                        arr[i][j] = moveArr[map[j]][i];
                    }
                    arr[i][k] = numbers[i];
                }
                var ret = GaussianElimination(arr);
                if (ret != 0) {
                    continue;
                }
                var isSolved = true;
                for (var i = k; i < 14; i++) {
                    if (arr[i][k] != 0) {
                        isSolved = false;
                        break;
                    }
                }
                if (!isSolved) {
                    continue;
                }
                backSubstitution(arr);
                var cnt_nz = 0;
                for (var i = 0; i < k; i++) {
                    if (arr[i][k] != 0) {
                        cnt_nz++;
                    }
                }
                if (cnt_nz < min_nz) {
                    for (var i = 0; i < 18; i++) {
                        solution[i] = 0;
                    }
                    for (var i = 0; i < k; i++) {
                        solution[map[i]] = arr[i][k];
                    }
                    min_nz = cnt_nz;
                }
            }
            return min_nz == k + 1 ? -1 : min_nz;
        }

        function GaussianElimination(arr) {
            var m = 14;
            var n = arr[0].length;
            for (var i = 0; i < n - 1; i++) {
                if (invert[arr[i][i]] == -1) {
                    var ivtidx = -1;
                    for (var j = i + 1; j < m; j++) {
                        if (invert[arr[j][i]] != -1) {
                            ivtidx = j;
                            break;
                        }
                    }
                    if (ivtidx == -1) {
                        OUT: for (var j1 = i; j1 < m - 1; j1++) {
                            for (var j2 = j1 + 1; j2 < m; j2++) {
                                if (invert[(arr[j1][i] + arr[j2][i]) % 12] != -1) {
                                    addTo(arr, j2, j1, i, 1);
                                    ivtidx = j1;
                                    break OUT;
                                }
                            }
                        }
                    }
                    if (ivtidx == -1) { //k vectors are linearly dependent
                        for (var j = i + 1; j < m; j++) {
                            if (arr[j][i] != 0) {
                                return -1;
                            }
                        }
                        return i + 1;
                    }
                    swap(arr, i, ivtidx);
                }
                var inv = invert[arr[i][i]];
                for (var j = i; j < n; j++) {
                    arr[i][j] = arr[i][j] * inv % 12;
                }
                for (var j = i + 1; j < m; j++) {
                    addTo(arr, i, j, i, 12 - arr[j][i]);
                }
            }
            return 0;
        }

        function backSubstitution(arr) {
            var n = arr[0].length;
            for (var i = n - 2; i > 0; i--) {
                for (var j = i - 1; j >= 0; j--) {
                    if (arr[j][i] != 0) {
                        addTo(arr, i, j, i, 12 - arr[j][i]);
                    }
                }
            }
        }

        return {
            moveArr: moveArr
        }

    })(mathlib.rn, mathlib.Cnk);

    var image = (function() {

        var scalingFactor = 10;

        var canvas, ctx;
        var hsq3 = Math.sqrt(3) / 2;
        var PI = Math.PI;

        var scrambleReg = /^([\d])?([FRUBLDfrubldzxySME])(?:([w])|&sup([\d]);)?([2'])?$/;

        function parseScramble(scramble, moveMap) {
            var moveseq = [];
            var moves = ("" + ' ' + scramble).split(' ');
            var m, w, f, p;
            for (var s=0; s<moves.length; s++) {
                m = scrambleReg.exec(moves[s]);
                if (m == null) {
                    continue;
                }
                f = "FRUBLDfrubldzxySME".indexOf(m[2]);
                if (f > 14) {
                    p = "2'".indexOf(m[5] || 'X') + 2;
                    f = [0, 4, 5][f % 3];
                    moveseq.push([moveMap.indexOf("FRUBLD".charAt(f)), 2, p]);
                    moveseq.push([moveMap.indexOf("FRUBLD".charAt(f)), 1, 4-p]);
                    continue;
                }
                w = f < 12 ? (~~m[1] || ~~m[4] || ((m[3] == "w" || f > 5) && 2) || 1) : -1;
                p = (f < 12 ? 1 : -1) * ("2'".indexOf(m[5] || 'X') + 2);
                moveseq.push([moveMap.indexOf("FRUBLD".charAt(f % 6)), w, p]);
            }
            return moveseq;
        }

        function Rotate(arr, theta) {
            return Transform(arr, [Math.cos(theta), -Math.sin(theta), 0, Math.sin(theta), Math.cos(theta), 0]);
        }

        function Transform(arr) {
            var ret;
            for (var i = 1; i < arguments.length; i++) {
                var trans = arguments[i];
                if (trans.length == 3) {
                    trans = [trans[0], 0, trans[1] * trans[0], 0, trans[0], trans[2] * trans[0]];
                }
                ret = [
                    [],
                    []
                ];
                for (var i = 0; i < arr[0].length; i++) {
                    ret[0][i] = arr[0][i] * trans[0] + arr[1][i] * trans[1] + trans[2];
                    ret[1][i] = arr[0][i] * trans[3] + arr[1][i] * trans[4] + trans[5];
                }
            }
            return ret;
        }

        function drawRoundedPolygon(ctx, pts, radius, color, do_override, overrides) {
            ctx.beginPath();
            ctx.fillStyle = color;
            if(color == TRANSPARENT) {
                ctx.strokeStyle = TRANSPARENT;
            } else {
                ctx.strokeStyle = "#000";
            }

            console.log(pts);

            if (radius > 0) {
                pts = getRoundedPoints(pts, radius, do_override, overrides);
            }

            var i, pt, len = pts.length;
            for (i = 0; i < len; i++) {
                pt = pts[i];
                if (i == 0) {
                    ctx.moveTo(pt[0], pt[1]);
                } else {
                    ctx.lineTo(pt[0], pt[1]);
                }
                if (radius > 0) {
                    ctx.quadraticCurveTo(pt[2], pt[3], pt[4], pt[5]);
                }
            }

            ctx.closePath();
            ctx.fill();
            ctx.stroke();
        }

        function getRoundedPoints(pts, radius, do_override, overrides) {
            var i1, i2, i3, p1, p2, p3, prevPt, nextPt,
                len = pts.length,
                res = new Array(len);
            for (i2 = 0; i2 < len; i2++) {
              i1 = i2-1;
              i3 = i2+1;
              if (i1 < 0) {
                i1 = len - 1;
              }
              if (i3 == len) {
                i3 = 0;
              }
              p1 = pts[i1];
              p2 = pts[i2];
              p3 = pts[i3];

              if (do_override) {
                used_radius = overrides[i2];
              } else {
                used_radius = radius;
              }

              prevPt = getRoundedPoint(p1[0], p1[1], p2[0], p2[1], used_radius, false);
              nextPt = getRoundedPoint(p2[0], p2[1], p3[0], p3[1], used_radius, true);
              res[i2] = [prevPt[0], prevPt[1], p2[0], p2[1], nextPt[0], nextPt[1]];
            }
            console.log(res);
            console.log('\n');
            return res;
        };

        function getRoundedPoint(x1, y1, x2, y2, radius, first) {
            var total = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2)),
                idx = first ? radius / total : (total - radius) / total;
            return [x1 + (idx * (x2 - x1)), y1 + (idx * (y2 - y1))];
        }

        // trans: [size, offx, offy] == [size, 0, offx * size, 0, size, offy * size] or [a11 a12 a13 a21 a22 a23]
        function drawPolygon(ctx, color, arr, trans, text, do_override, overrides) {
            if (!ctx) {
                return;
            }

            do_override = do_override || false;
            overrides = overrides || [];

            trans = trans || [1, 0, 0, 0, 1, 0];
            arr = Transform(arr, trans);

            var ptsByXY = [];
            var xPts = arr[0];
            var yPts = arr[1];
            for (var i = 0; i < xPts.length; i++) {
                ptsByXY[i] = [xPts[i], yPts[i]];
            }

            drawRoundedPolygon(ctx, ptsByXY, eventCornerRadius, color, do_override, overrides);

            if (text) {
                ctx.fillStyle = '#000';
                ctx.strokeStyle = '#000';
                ctx.fillText(text, arr[0][0], arr[1][0]);
            }
        }

        var mgmImage = (function() {
            var moveU = [4, 0, 1, 2, 3, 9, 5, 6, 7, 8, 10, 11, 12, 13, 58, 59, 16, 17, 18, 63, 20, 21, 22, 23, 24, 14, 15, 27, 28, 29, 19, 31, 32, 33, 34, 35, 25, 26, 38, 39, 40, 30, 42, 43, 44, 45, 46, 36, 37, 49, 50, 51, 41, 53, 54, 55, 56, 57, 47, 48, 60, 61, 62, 52, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131];
            var moveR = [81, 77, 78, 3, 4, 86, 82, 83, 8, 85, 87, 122, 123, 124, 125, 121, 127, 128, 129, 130, 126, 131, 89, 90, 24, 25, 88, 94, 95, 29, 97, 93, 98, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 26, 22, 23, 48, 30, 31, 27, 28, 53, 32, 69, 70, 66, 67, 68, 74, 75, 71, 72, 73, 76, 101, 102, 103, 99, 100, 106, 107, 108, 104, 105, 109, 46, 47, 79, 80, 45, 51, 52, 84, 49, 50, 54, 0, 1, 2, 91, 92, 5, 6, 7, 96, 9, 10, 15, 11, 12, 13, 14, 20, 16, 17, 18, 19, 21, 113, 114, 110, 111, 112, 118, 119, 115, 116, 117, 120, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65];
            var moveD = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 33, 34, 35, 14, 15, 38, 39, 40, 19, 42, 43, 44, 45, 46, 25, 26, 49, 50, 51, 30, 53, 54, 55, 56, 57, 36, 37, 60, 61, 62, 41, 64, 65, 11, 12, 13, 47, 48, 16, 17, 18, 52, 20, 21, 22, 23, 24, 58, 59, 27, 28, 29, 63, 31, 32, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 124, 125, 121, 122, 123, 129, 130, 126, 127, 128, 131];
            var moveMaps = [moveU, moveR, moveD];

            var width = 40;
            var cfrac = 0.5;
            var efrac2 = (Math.sqrt(5) + 1) / 2;
            var d2x = (1 - cfrac) / 2 / Math.tan(PI / 5);
            var off1X = 2.6;
            var off1Y = 2.2;
            var off2X = off1X + Math.cos(PI * 0.1) * 3 * efrac2;
            var off2Y = off1Y + Math.sin(PI * 0.1) * 1 * efrac2;
            var cornX = [0, d2x, 0, -d2x];
            var cornY = [-1, -(1 + cfrac) / 2, -cfrac, -(1 + cfrac) / 2];
            var edgeX = [Math.cos(PI * 0.1) - d2x, d2x, 0, Math.sin(PI * 0.4) * cfrac];
            var edgeY = [-Math.sin(PI * 0.1) + (cfrac - 1) / 2, -(1 + cfrac) / 2, -cfrac, -Math.cos(PI * 0.4) * cfrac];
            var centX = [Math.sin(PI * 0.0) * cfrac, Math.sin(PI * 0.4) * cfrac, Math.sin(PI * 0.8) * cfrac, Math.sin(PI * 1.2) * cfrac, Math.sin(PI * 1.6) * cfrac];
            var centY = [-Math.cos(PI * 0.0) * cfrac, -Math.cos(PI * 0.4) * cfrac, -Math.cos(PI * 0.8) * cfrac, -Math.cos(PI * 1.2) * cfrac, -Math.cos(PI * 1.6) * cfrac];
            var colors = null;

            function drawFace(state, baseIdx, trans, rot) {

                setColors();
                colors = mega_colors;

                for (var i = 0; i < 5; i++) {
                    drawPolygon(ctx, colors[state[baseIdx + i]], Rotate([cornX, cornY], PI * 2 / 5 * i + rot), trans);
                    drawPolygon(ctx, colors[state[baseIdx + i + 5]], Rotate([edgeX, edgeY], PI * 2 / 5 * i + rot), trans);
                }
                drawPolygon(ctx, colors[state[baseIdx + 10]], Rotate([centX, centY], rot), trans);
            }

            function doMove(state, axis, inv) {
                var moveMap = moveMaps[axis];
                var oldState = state.slice();
                if (inv) {
                    for (var i = 0; i < 132; i++) {
                        state[moveMap[i]] = oldState[i];
                    }
                } else {
                    for (var i = 0; i < 132; i++) {
                        state[i] = oldState[moveMap[i]];
                    }
                }
            }

            var movere = /[RD][+-]{2}|U'?/
            return function(moveseq) {
                var state = [];
                for (var i = 0; i < 12; i++) {
                    for (var j = 0; j < 11; j++) {
                        state[i * 11 + j] = i;
                    }
                }
                var moves = moveseq.split(/\s+/);
                for (var i = 0; i < moves.length; i++) {
                    var m = movere.exec(moves[i]);
                    if (!m) {
                        continue;
                    }
                    var axis = "URD".indexOf(m[0][0]);
                    var inv = /[-']/.exec(m[0][1]);
                    doMove(state, axis, inv);
                }
                var imgSize = scalingFactor / 7.5;
                canvas.width(7 * imgSize + 'em');
                canvas.height(3.5 * imgSize + 'em');
                canvas.attr('width', 9.8 * width);
                canvas.attr('height', 4.9 * width);
                drawFace(state, 0, [width, off1X + 0 * efrac2, off1Y + 0 * efrac2], PI * 0.0);
                drawFace(state, 11, [width, off1X + Math.cos(PI * 0.1) * efrac2, off1Y + Math.sin(PI * 0.1) * efrac2], PI * 0.2);
                drawFace(state, 22, [width, off1X + Math.cos(PI * 0.5) * efrac2, off1Y + Math.sin(PI * 0.5) * efrac2], PI * 0.6);
                drawFace(state, 33, [width, off1X + Math.cos(PI * 0.9) * efrac2, off1Y + Math.sin(PI * 0.9) * efrac2], PI * 1.0);
                drawFace(state, 44, [width, off1X + Math.cos(PI * 1.3) * efrac2, off1Y + Math.sin(PI * 1.3) * efrac2], PI * 1.4);
                drawFace(state, 55, [width, off1X + Math.cos(PI * 1.7) * efrac2, off1Y + Math.sin(PI * 1.7) * efrac2], PI * 1.8);
                drawFace(state, 66, [width, off2X + Math.cos(PI * 0.7) * efrac2, off2Y + Math.sin(PI * 0.7) * efrac2], PI * 0.0);
                drawFace(state, 77, [width, off2X + Math.cos(PI * 0.3) * efrac2, off2Y + Math.sin(PI * 0.3) * efrac2], PI * 1.6);
                drawFace(state, 88, [width, off2X + Math.cos(PI * 1.9) * efrac2, off2Y + Math.sin(PI * 1.9) * efrac2], PI * 1.2);
                drawFace(state, 99, [width, off2X + Math.cos(PI * 1.5) * efrac2, off2Y + Math.sin(PI * 1.5) * efrac2], PI * 0.8);
                drawFace(state, 110, [width, off2X + Math.cos(PI * 1.1) * efrac2, off2Y + Math.sin(PI * 1.1) * efrac2], PI * 0.4);
                drawFace(state, 121, [width, off2X + 0 * efrac2, off2Y + 0 * efrac2], PI * 1.0);
                if (ctx) {
                    ctx.fillStyle = "#000";
                    ctx.font = "20px serif";
                    ctx.textAlign = "center";
                    ctx.textBaseline = "middle";
                    ctx.fillText("U", width * off1X, width * off1Y);
                    ctx.fillText("F", width * off1X, width * (off1Y + Math.sin(PI * 0.5) * efrac2));
                }
            };
        })();

        var kilominxImage = (function() {
            var moveU = [4, 0, 1, 2, 3, 9, 5, 6, 7, 8, 10, 11, 12, 13, 58, 59, 16, 17, 18, 63, 20, 21, 22, 23, 24, 14, 15, 27, 28, 29, 19, 31, 32, 33, 34, 35, 25, 26, 38, 39, 40, 30, 42, 43, 44, 45, 46, 36, 37, 49, 50, 51, 41, 53, 54, 55, 56, 57, 47, 48, 60, 61, 62, 52, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131];
            var moveR = [81, 77, 78, 3, 4, 86, 82, 83, 8, 85, 87, 122, 123, 124, 125, 121, 127, 128, 129, 130, 126, 131, 89, 90, 24, 25, 88, 94, 95, 29, 97, 93, 98, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 26, 22, 23, 48, 30, 31, 27, 28, 53, 32, 69, 70, 66, 67, 68, 74, 75, 71, 72, 73, 76, 101, 102, 103, 99, 100, 106, 107, 108, 104, 105, 109, 46, 47, 79, 80, 45, 51, 52, 84, 49, 50, 54, 0, 1, 2, 91, 92, 5, 6, 7, 96, 9, 10, 15, 11, 12, 13, 14, 20, 16, 17, 18, 19, 21, 113, 114, 110, 111, 112, 118, 119, 115, 116, 117, 120, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65];
            var moveD = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 33, 34, 35, 14, 15, 38, 39, 40, 19, 42, 43, 44, 45, 46, 25, 26, 49, 50, 51, 30, 53, 54, 55, 56, 57, 36, 37, 60, 61, 62, 41, 64, 65, 11, 12, 13, 47, 48, 16, 17, 18, 52, 20, 21, 22, 23, 24, 58, 59, 27, 28, 29, 63, 31, 32, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 124, 125, 121, 122, 123, 129, 130, 126, 127, 128, 131];
            var moveMaps = [moveU, moveR, moveD];

            var width = 40;
            var cfrac = 0.33;
            var efrac2 = (Math.sqrt(5) + 1) / 2;
            var d2x = (1 - cfrac) / 2 / Math.tan(PI / 5);
            var off1X = 2.6;
            var off1Y = 2.2;
            var off2X = off1X + Math.cos(PI * 0.1) * 3 * efrac2;
            var off2Y = off1Y + Math.sin(PI * 0.1) * 1 * efrac2;
            var cornX = [0, d2x, 0, -d2x];
            var cornY = [-1, -(1 + cfrac) / 2, -cfrac * 0.25, -(1 + cfrac) / 2];
            var edgeX = [Math.cos(PI * 0.1) - d2x, d2x, 0, Math.sin(PI * 0.4) * cfrac];
            var edgeY = [-Math.sin(PI * 0.1) + (cfrac - 1) / 2, -(1 + cfrac) / 2, -cfrac, -Math.cos(PI * 0.4) * cfrac];
            var centX = [Math.sin(PI * 0.0) * cfrac, Math.sin(PI * 0.4) * cfrac, Math.sin(PI * 0.8) * cfrac, Math.sin(PI * 1.2) * cfrac, Math.sin(PI * 1.6) * cfrac];
            var centY = [-Math.cos(PI * 0.0) * cfrac, -Math.cos(PI * 0.4) * cfrac, -Math.cos(PI * 0.8) * cfrac, -Math.cos(PI * 1.2) * cfrac, -Math.cos(PI * 1.6) * cfrac];
            var colors = null;

            function drawFace(state, baseIdx, trans, rot) {

                if (!colors) {
                    setColors();
                    colors = mega_colors;
                }

                // draw "centers" and "edges" first, as black, so they just appear as background fill
                // after the corners draw on top of them
                drawPolygon(ctx, '#000000', Rotate([centX, centY], rot), trans);
                for (var i = 0; i < 5; i++) {
                    drawPolygon(ctx, '#000000', Rotate([edgeX, edgeY], PI * 2 / 5 * i + rot), trans);
                }

                for (var i = 0; i < 5; i++) {
                    drawPolygon(ctx, colors[state[baseIdx + i]], Rotate([cornX, cornY], PI * 2 / 5 * i + rot), trans);
                }
            }

            function doMove(state, axis, inv) {
                var moveMap = moveMaps[axis];
                var oldState = state.slice();
                if (inv) {
                    for (var i = 0; i < 132; i++) {
                        state[moveMap[i]] = oldState[i];
                    }
                } else {
                    for (var i = 0; i < 132; i++) {
                        state[i] = oldState[moveMap[i]];
                    }
                }
            }

            var movere = /[RD][+-]{2}|U'?/
            return function(moveseq) {
                var state = [];
                for (var i = 0; i < 12; i++) {
                    for (var j = 0; j < 11; j++) {
                        state[i * 11 + j] = i;
                    }
                }
                var moves = moveseq.split(/\s+/);
                for (var i = 0; i < moves.length; i++) {
                    var m = movere.exec(moves[i]);
                    if (!m) {
                        continue;
                    }
                    var axis = "URD".indexOf(m[0][0]);
                    var inv = /[-']/.exec(m[0][1]);
                    doMove(state, axis, inv);
                }
                var imgSize = scalingFactor / 7.5;
                canvas.width(7 * imgSize + 'em');
                canvas.height(3.5 * imgSize + 'em');
                canvas.attr('width', 9.8 * width);
                canvas.attr('height', 4.9 * width);
                drawFace(state, 0, [width, off1X + 0 * efrac2, off1Y + 0 * efrac2], PI * 0.0);
                drawFace(state, 11, [width, off1X + Math.cos(PI * 0.1) * efrac2, off1Y + Math.sin(PI * 0.1) * efrac2], PI * 0.2);
                drawFace(state, 22, [width, off1X + Math.cos(PI * 0.5) * efrac2, off1Y + Math.sin(PI * 0.5) * efrac2], PI * 0.6);
                drawFace(state, 33, [width, off1X + Math.cos(PI * 0.9) * efrac2, off1Y + Math.sin(PI * 0.9) * efrac2], PI * 1.0);
                drawFace(state, 44, [width, off1X + Math.cos(PI * 1.3) * efrac2, off1Y + Math.sin(PI * 1.3) * efrac2], PI * 1.4);
                drawFace(state, 55, [width, off1X + Math.cos(PI * 1.7) * efrac2, off1Y + Math.sin(PI * 1.7) * efrac2], PI * 1.8);
                drawFace(state, 66, [width, off2X + Math.cos(PI * 0.7) * efrac2, off2Y + Math.sin(PI * 0.7) * efrac2], PI * 0.0);
                drawFace(state, 77, [width, off2X + Math.cos(PI * 0.3) * efrac2, off2Y + Math.sin(PI * 0.3) * efrac2], PI * 1.6);
                drawFace(state, 88, [width, off2X + Math.cos(PI * 1.9) * efrac2, off2Y + Math.sin(PI * 1.9) * efrac2], PI * 1.2);
                drawFace(state, 99, [width, off2X + Math.cos(PI * 1.5) * efrac2, off2Y + Math.sin(PI * 1.5) * efrac2], PI * 0.8);
                drawFace(state, 110, [width, off2X + Math.cos(PI * 1.1) * efrac2, off2Y + Math.sin(PI * 1.1) * efrac2], PI * 0.4);
                drawFace(state, 121, [width, off2X + 0 * efrac2, off2Y + 0 * efrac2], PI * 1.0);
            };
        })();

        var clkImage = (function() {
            function drawClock(color, trans, time) {
                if (!ctx) {
                    return;
                }
                var points = Transform(Rotate([
                    [1, 1, 0, -1, -1, -1, 1, 0],
                    [0, -1, -8, -1, 0, 1, 1, 0]
                ], time / 6 * PI), trans);
                var x = points[0];
                var y = points[1];

                ctx.beginPath();
                ctx.fillStyle = color;
                ctx.arc(x[7], y[7], trans[0] * 9, 0, 2 * PI);
                ctx.fill();

                ctx.beginPath();
                ctx.fillStyle = '#ff0';
                ctx.strokeStyle = '#f00';
                ctx.moveTo(x[0], y[0]);
                ctx.bezierCurveTo(x[1], y[1], x[1], y[1], x[2], y[2]);
                ctx.bezierCurveTo(x[3], y[3], x[3], y[3], x[4], y[4]);
                ctx.bezierCurveTo(x[5], y[5], x[6], y[6], x[0], y[0]);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();
            }

            function drawButton(color, trans) {
                if (!ctx) {
                    return;
                }
                var points = Transform([
                    [0],
                    [0]
                ], trans);
                ctx.beginPath();
                ctx.fillStyle = color;
                ctx.strokeStyle = '#000';
                ctx.arc(points[0][0], points[1][0], trans[0] * 3, 0, 2 * PI);
                ctx.fill();
                ctx.stroke();
            }

            var width = 3;
            var movere = /([UD][RL]|ALL|[UDRLy])(\d[+-]?)?/
            var movestr = ['UR', 'DR', 'DL', 'UL', 'U', 'R', 'D', 'L', 'ALL']

            return function(moveseq) {
                var moves = moveseq.split(/\s+/);
                var moveArr = clock.moveArr;
                var flip = 9;
                var buttons = [0, 0, 0, 0];
                var clks = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
                for (var i = 0; i < moves.length; i++) {
                    var m = movere.exec(moves[i]);
                    if (!m) {
                        continue;
                    }
                    if (m[0] == 'y2') {
                        flip = 0;
                        continue;
                    }
                    var axis = movestr.indexOf(m[1]) + flip;
                    if (m[2] == undefined) {
                        buttons[axis % 9] = 1;
                        continue;
                    }
                    var power = ~~m[2][0];
                    power = m[2][1] == '+' ? power : 12 - power;
                    for (var j = 0; j < 14; j++) {
                        clks[j] = (clks[j] + moveArr[axis][j] * power) % 12;
                    }
                }
                clks = [clks[0], clks[3], clks[6], clks[1], clks[4], clks[7], clks[2], clks[5], clks[8],
                    12 - clks[2], clks[10], 12 - clks[8], clks[9], clks[11], clks[13], 12 - clks[0], clks[12], 12 - clks[6]
                ];
                buttons = [buttons[3], buttons[2], buttons[0], buttons[1], 1 - buttons[0], 1 - buttons[1], 1 - buttons[3], 1 - buttons[2]];

                var imgSize = scalingFactor / 7.5;
                canvas.width(6.25 * imgSize + 'em');
                canvas.height(3 * imgSize + 'em');
                canvas.attr('width', 6.25 * 20 * width);
                canvas.attr('height', 3 * 20 * width);

                var y = [10, 30, 50];
                var x = [10, 30, 50, 75, 95, 115];
                for (var i = 0; i < 18; i++) {
                    drawClock(['#37b', '#5cf'][~~(i / 9)], [width, x[~~(i / 3)], y[i % 3]], clks[i]);
                }

                var y = [20, 40];
                var x = [20, 40, 85, 105];
                for (var i = 0; i < 8; i++) {
                    drawButton(['#850', '#ff0'][buttons[i]], [width, x[~~(i / 2)], y[i % 2]]);
                }
            };
        })();


        var sq1Image = (function() {
            var posit = [];
            var mid = 0;
            var colors = null;

            //(move[0], move[1]) (/ = move[2])
            function doMove(move) {
                var newposit = [];

                //top move
                for (var i = 0; i < 12; i++) {
                    newposit[(i + move[0]) % 12] = posit[i];
                }

                //bottom move
                for (var i = 0; i < 12; i++) {
                    newposit[i + 12] = posit[(i + move[1]) % 12 + 12];
                }

                if (move[2]) {
                    mid = 1 - mid;
                    for (var i = 0; i < 6; i++) {
                        mathlib.circle(newposit, i + 6, 23 - i);
                    }
                }
                posit = newposit;
            }

            var ep = [
                [0, -0.5, 0.5],
                [0, -hsq3 - 1, -hsq3 - 1]
            ];
            var cp = [
                [0, -0.5, -hsq3 - 1, -hsq3 - 1],
                [0, -hsq3 - 1, -hsq3 - 1, -0.5]
            ];
            var cpr = [
                [0, -0.5, -hsq3 - 1],
                [0, -hsq3 - 1, -hsq3 - 1]
            ];
            var cpl = [
                [0, -hsq3 - 1, -hsq3 - 1],
                [0, -hsq3 - 1, -0.5]
            ];

            var eps = Transform(ep, [0.66, 0, 0]);
            var cps = Transform(cp, [0.66, 0, 0]);

            var udcol = 'UD';
            var ecol = '-B-R-F-L-B-R-F-L';
            var ccol = 'LBBRRFFLBLRBFRLF';
            var colors = null;

            var width = 45;

            var movere = /^\s*\(\s*(-?\d+),\s*(-?\d+)\s*\)\s*$/

            return function(moveseq) {

                setColors();
                colors = sq1_colors;

                posit = [0, 0, 1, 2, 2, 3, 4, 4, 5, 6, 6, 7, 8, 8, 9, 10, 10, 11, 12, 12, 13, 14, 14, 15];
                mid = 0;
                var moves = moveseq.split('/');
                for (var i = 0; i < moves.length; i++) {
                    if (/^\s*$/.exec(moves[i])) {
                        doMove([0, 0, 1]);
                        continue;
                    }
                    var m = movere.exec(moves[i]);
                    doMove([~~m[1] + 12, ~~m[2] + 12, 1]);
                }
                doMove([0, 0, 1]);


                var imgSize = scalingFactor / 10;
                canvas.width(11 * imgSize / 1.3 + 'em');
                canvas.height(6.3 * imgSize / 1.3 + 'em');

                canvas.attr('width', 11 * width);
                canvas.attr('height', 6.3 * width);

                var trans = [width, 2.7, 2.7];
                //draw top
                for (var i = 0; i < 12; i++) {
                    if (posit[i] % 2 == 0) { //corner piece
                        if (posit[i] != posit[(i + 1) % 12]) {
                            continue;
                        }
                        drawPolygon(ctx, colors[ccol[posit[i]]],
                            Rotate(cpl, (i - 3) * PI / 6), trans);
                        drawPolygon(ctx, colors[ccol[posit[i] + 1]],
                            Rotate(cpr, (i - 3) * PI / 6), trans);
                        drawPolygon(ctx, colors[udcol[posit[i] >= 8 ? 1 : 0]],
                            Rotate(cps, (i - 3) * PI / 6), trans);
                    } else { //edge piece
                        drawPolygon(ctx, colors[ecol[posit[i]]],
                            Rotate(ep, (i - 5) * PI / 6), trans);
                        drawPolygon(ctx, colors[udcol[posit[i] >= 8 ? 1 : 0]],
                            Rotate(eps, (i - 5) * PI / 6), trans);
                    }
                }

                var trans = [width, 2.7 + 5.4, 2.7];
                //draw bottom
                for (var i = 12; i < 24; i++) {
                    if (posit[i] % 2 == 0) { //corner piece
                        if (posit[i] != posit[(i + 1) % 12 + 12]) {
                            continue;
                        }
                        drawPolygon(ctx, colors[ccol[posit[i]]],
                            Rotate(cpl, -i * PI / 6), trans);
                        drawPolygon(ctx, colors[ccol[posit[i] + 1]],
                            Rotate(cpr, -i * PI / 6), trans);
                        drawPolygon(ctx, colors[udcol[posit[i] >= 8 ? 1 : 0]],
                            Rotate(cps, -i * PI / 6), trans);
                    } else { //edge piece
                        drawPolygon(ctx, colors[ecol[posit[i]]],
                            Rotate(ep, (-1 - i) * PI / 6), trans);
                        drawPolygon(ctx, colors[udcol[posit[i] >= 8 ? 1 : 0]],
                            Rotate(eps, (-1 - i) * PI / 6), trans);
                    }
                }

                var trans = [width, 2.7 + 2.7, 2.7 + 3.0];
                //draw middle
                drawPolygon(ctx, colors['L'], [[-hsq3 - 1, -hsq3 - 1, -0.5, -0.5], [0.5, -0.5, -0.5, 0.5]], trans);
                if (mid == 0) {
                    drawPolygon(ctx, colors['L'], [[hsq3 + 1, hsq3 + 1, -0.5, -0.5], [0.5, -0.5, -0.5, 0.5]], trans);
                } else {
                    drawPolygon(ctx, colors['R'], [[hsq3, hsq3, -0.5, -0.5], [0.5, -0.5, -0.5, 0.5]], trans);
                }
            }
        })();

        var skewbImage = (function() {
            var width = 45;
            var gap = width / 10;
            var posit = [];

            var colors = null;

            var ftrans = [
                [width * hsq3, width * hsq3, (width * 4 + gap * 1.5) * hsq3, -width / 2, width / 2, width],
                [width * hsq3, 0, (width * 7 + gap * 3) * hsq3, -width / 2, width, width * 1.5],
                [width * hsq3, 0, (width * 5 + gap * 2) * hsq3, -width / 2, width, width * 2.5 + 0.5 * gap],
                [0, -width * hsq3, (width * 3 + gap * 1) * hsq3, width, -width / 2, width * 4.5 + 1.5 * gap],
                [width * hsq3, 0, (width * 3 + gap * 1) * hsq3, width / 2, width, width * 2.5 + 0.5 * gap],
                [width * hsq3, 0, width * hsq3, width / 2, width, width * 1.5]
            ];

            function doMove(axis, power) {
                for (var p = 0; p < power; p++) {
                    switch (axis) {
                        case 0: //R
                            mathlib.circle(posit, 2 * 5 + 0, 1 * 5 + 0, 3 * 5 + 0);
                            mathlib.circle(posit, 2 * 5 + 4, 1 * 5 + 3, 3 * 5 + 2);
                            mathlib.circle(posit, 2 * 5 + 2, 1 * 5 + 4, 3 * 5 + 1);
                            mathlib.circle(posit, 2 * 5 + 3, 1 * 5 + 1, 3 * 5 + 4);
                            mathlib.circle(posit, 4 * 5 + 4, 0 * 5 + 4, 5 * 5 + 3);
                            break;
                        case 1: //U
                            mathlib.circle(posit, 0 * 5 + 0, 5 * 5 + 0, 1 * 5 + 0);
                            mathlib.circle(posit, 0 * 5 + 2, 5 * 5 + 1, 1 * 5 + 2);
                            mathlib.circle(posit, 0 * 5 + 4, 5 * 5 + 2, 1 * 5 + 4);
                            mathlib.circle(posit, 0 * 5 + 1, 5 * 5 + 3, 1 * 5 + 1);
                            mathlib.circle(posit, 4 * 5 + 1, 3 * 5 + 4, 2 * 5 + 2);
                            break;
                        case 2: //L
                            mathlib.circle(posit, 4 * 5 + 0, 3 * 5 + 0, 5 * 5 + 0);
                            mathlib.circle(posit, 4 * 5 + 3, 3 * 5 + 3, 5 * 5 + 4);
                            mathlib.circle(posit, 4 * 5 + 1, 3 * 5 + 1, 5 * 5 + 3);
                            mathlib.circle(posit, 4 * 5 + 4, 3 * 5 + 4, 5 * 5 + 2);
                            mathlib.circle(posit, 2 * 5 + 3, 1 * 5 + 4, 0 * 5 + 1);
                            break;
                        case 3: //B
                            mathlib.circle(posit, 1 * 5 + 0, 5 * 5 + 0, 3 * 5 + 0);
                            mathlib.circle(posit, 1 * 5 + 4, 5 * 5 + 3, 3 * 5 + 4);
                            mathlib.circle(posit, 1 * 5 + 3, 5 * 5 + 1, 3 * 5 + 3);
                            mathlib.circle(posit, 1 * 5 + 2, 5 * 5 + 4, 3 * 5 + 2);
                            mathlib.circle(posit, 0 * 5 + 2, 4 * 5 + 3, 2 * 5 + 4);
                            break;
                    }
                }
            }

            function face(f) {

                if (!colors) {
                    setColors();
                    colors = skewb_colors;
                }

                var transform = ftrans[f];
                drawPolygon(ctx, colors[posit[f * 5 + 0]], [
                    [-1, 0, 1, 0],
                    [0, 1, 0, -1]
                ], transform);
                drawPolygon(ctx, colors[posit[f * 5 + 1]], [
                    [-1, -1, 0],
                    [0, -1, -1]
                ], transform);
                drawPolygon(ctx, colors[posit[f * 5 + 2]], [
                    [0, 1, 1],
                    [-1, -1, 0]
                ], transform);
                drawPolygon(ctx, colors[posit[f * 5 + 3]], [
                    [-1, -1, 0],
                    [0, 1, 1]
                ], transform);
                drawPolygon(ctx, colors[posit[f * 5 + 4]], [
                    [0, 1, 1],
                    [1, 1, 0]
                ], transform);
            }

            return function(moveseq) {
                var cnt = 0;
                for (var i = 0; i < 6; i++) {
                    for (var f = 0; f < 5; f++) {
                        posit[cnt++] = i;
                    }
                }
                var scramble = parseScramble(moveseq, 'RULB');
                for (var i = 0; i < scramble.length; i++) {
                    doMove(scramble[i][0], scramble[i][2] == 1 ? 1 : 2);
                }
                var imgSize = scalingFactor / 10;
                canvas.width((8 * hsq3 + 0.3) * imgSize + 'em');
                canvas.height(6.2 * imgSize + 'em');

                canvas.attr('width', (8 * hsq3 + 0.3) * width + 1);
                canvas.attr('height', 6.2 * width + 1);

                for (var i = 0; i < 6; i++) {
                    face(i);
                }
            }
        })();

        var rexImage = (function() {
            var width = 45;
            var gap = width / 10;
            var posit = [];

            var colors = null;

            var ftrans = [
                [width * hsq3, width * hsq3, (width * 4 + gap * 1.5) * hsq3, -width / 2, width / 2, width],
                [width * hsq3, 0, (width * 7 + gap * 3) * hsq3, -width / 2, width, width * 1.5],
                [width * hsq3, 0, (width * 5 + gap * 2) * hsq3, -width / 2, width, width * 2.5 + 0.5 * gap],
                [0, -width * hsq3, (width * 3 + gap * 1) * hsq3, width, -width / 2, width * 4.5 + 1.5 * gap],
                [width * hsq3, 0, (width * 3 + gap * 1) * hsq3, width / 2, width, width * 2.5 + 0.5 * gap],
                [width * hsq3, 0, width * hsq3, width / 2, width, width * 1.5]
            ];

            function doMove(move) {
                if (move == 'F') {
                    mathlib.circle(posit, 8, 26, 44); // centers
                    mathlib.circle(posit, 7, 24, 41); // left petals
                    mathlib.circle(posit, 5, 22, 43); // right petals
                    mathlib.circle(posit, 4, 25, 42); // inner petals
                    mathlib.circle(posit, 3, 18, 37); // left edges
                    mathlib.circle(posit, 2, 21, 36); // right edges
                }
                if (move == 'R') {
                    mathlib.circle(posit, 8, 17, 26); // centers
                    mathlib.circle(posit, 4, 15, 23); // left petals
                    mathlib.circle(posit, 6, 13, 25); // right petals
                    mathlib.circle(posit, 5, 16, 24); // inner petals
                    mathlib.circle(posit, 2, 9, 19); // left edges
                    mathlib.circle(posit, 1, 12, 18); // right edges}
                }
                if (move == 'L') {
                    mathlib.circle(posit, 8, 44, 53); // centers
                    mathlib.circle(posit, 6, 42, 50); // left petals
                    mathlib.circle(posit, 4, 40, 52); // right petals
                    mathlib.circle(posit, 7, 43, 51); // inner petals
                    mathlib.circle(posit, 0, 36, 46); // left edges
                    mathlib.circle(posit, 3, 39, 45); // right edges}
                }
                if (move == 'B') {
                    mathlib.circle(posit, 8, 53, 17); // centers
                    mathlib.circle(posit, 5, 51, 14); // left petals
                    mathlib.circle(posit, 7, 49, 16); // right petals
                    mathlib.circle(posit, 6, 52, 15); // inner petals
                    mathlib.circle(posit, 1, 45, 10); // left edges
                    mathlib.circle(posit, 0, 48, 9); // right edges}
                }
                if (move == 'f') {
                    mathlib.circle(posit, 44, 26, 35); // centers
                    mathlib.circle(posit, 40, 25, 33); // left petals
                    mathlib.circle(posit, 42, 23, 31); // right petals
                    mathlib.circle(posit, 41, 22, 34); // inner petals
                    mathlib.circle(posit, 38, 21, 27); // left edges
                    mathlib.circle(posit, 37, 20, 30); // right edges
                }
                if (move == 'r') {
                    mathlib.circle(posit, 26, 17, 35); // centers
                    mathlib.circle(posit, 22, 16, 32); // left petals
                    mathlib.circle(posit, 34, 24, 14); // right petals
                    mathlib.circle(posit, 33, 23, 13); // inner petals
                    mathlib.circle(posit, 28, 20, 12); // left edges
                    mathlib.circle(posit, 27, 19, 11); // right edges}
                }
                if (move == 'l') {
                    mathlib.circle(posit, 53, 44, 35); // centers
                    mathlib.circle(posit, 49, 43, 34); // left petals
                    mathlib.circle(posit, 51, 41, 32); // right petals
                    mathlib.circle(posit, 50, 40, 31); // inner petals
                    mathlib.circle(posit, 47, 39, 30); // left edges
                    mathlib.circle(posit, 46, 38, 29); // right edges}
                }
                if (move == 'b') {
                    mathlib.circle(posit, 17, 53, 35); // centers
                    mathlib.circle(posit, 52, 31, 13); // left petals
                    mathlib.circle(posit, 50, 33, 15); // right petals
                    mathlib.circle(posit, 49, 32, 14); // inner petals
                    mathlib.circle(posit, 48, 29, 11); // left edges
                    mathlib.circle(posit, 47, 28, 10); // right edges}
                }
            }

            function face(f) {

                setColors();
                colors = rex_colors;

                var transform = ftrans[f];

                // === Edges ===

                drawPolygon(ctx, colors[posit[f * 9 + 0]], [
                    [-1, 1, 0],
                    [-1, -1, 0]
                ], transform);

                drawPolygon(ctx, colors[posit[f * 9 + 1]], [
                    [1, 1, 0],
                    [-1, 1, 0]
                ], transform);

                drawPolygon(ctx, colors[posit[f * 9 + 2]], [
                    [1, -1, 0],
                    [1, 1, 0]
                ], transform);

                drawPolygon(ctx, colors[posit[f * 9 + 3]], [
                    [-1, -1, 0],
                    [1, -1, 0]
                ], transform);

                // === Petals ===

                // curve reference: https://bit.ly/3sHjYl8

                drawPolygon(ctx, colors[posit[f * 9 + 4]], [
                    [-1,  -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0, 0, -0.45, -0.5275, -0.6, -0.666, -0.726, -0.784, -0.835, -0.882, -0.926],
                    [1, 0.965, 0.926, 0.882, 0.835, 0.784, 0.726, 0.666, 0.6, 0.5275, 0.45, 0, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
                ], transform);

                drawPolygon(ctx, colors[posit[f * 9 + 5]], [
                    [1,  0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0, 0, 0.45, 0.5275, 0.6, 0.666, 0.726, 0.784, 0.835, 0.882, 0.926],
                    [1, 0.965, 0.926, 0.882, 0.835, 0.784, 0.726, 0.666, 0.6, 0.5275, 0.45, 0, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
                ], transform);

                drawPolygon(ctx, colors[posit[f * 9 + 6]], [
                    [1,  0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0, 0, 0.45, 0.5275, 0.6, 0.666, 0.726, 0.784, 0.835, 0.882, 0.926],
                    [-1, -0.965, -0.926, -0.882, -0.835, -0.784, -0.726, -0.666, -0.6, -0.5275, -0.45, 0, 0, -0.1, -0.2, -0.3, -0.4, -0.5, -0.6, -0.7, -0.8, -0.9]
                ], transform);

                drawPolygon(ctx, colors[posit[f * 9 + 7]], [
                    [-1,  -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0, 0, -0.45, -0.5275, -0.6, -0.666, -0.726, -0.784, -0.835, -0.882, -0.926],
                    [-1, -0.965, -0.926, -0.882, -0.835, -0.784, -0.726, -0.666, -0.6, -0.5275, -0.45, 0, 0, -0.1, -0.2, -0.3, -0.4, -0.5, -0.6, -0.7, -0.8, -0.9]
                ], transform);

                // === Center ===

                drawPolygon(ctx, colors[posit[f * 9 + 8]], [
                    [0, 0.1125, 0.225, 0.3375, 0.45, 0.3375, 0.225, 0.1125, 0, -0.1125, -0.225, -0.3375, -0.45, -0.3375, -0.225, -0.1125, 0],
                    [0.45, 0.353, 0.246, 0.13, 0, -0.13, -0.246, -0.353, -0.45, -0.353, -0.246, -0.13, 0, 0.13, 0.246, 0.353, 0.45]
                ], transform);
            }

            return function(moveseq) {
                var cnt = 0;
                for (var i = 0; i < 6; i++) {
                    for (var f = 0; f < 9; f++) {
                        posit[cnt++] = i;
                    }
                }

                var scramble = moveseq.split(' ');
                for (var i = 0; i < scramble.length; i++) {
                    var move = scramble[i];
                    if (move.endsWith("'")) {
                        move = move.replace("'", "");
                        // U' == U U
                        doMove(move);
                        doMove(move);
                    } else {
                        doMove(move);
                    }
                }

                var imgSize = scalingFactor / 10;
                canvas.width((8 * hsq3 + 0.3) * imgSize + 'em');
                canvas.height(6.2 * imgSize + 'em');

                canvas.attr('width', (8 * hsq3 + 0.3) * width + 1);
                canvas.attr('height', 6.2 * width + 1);

                for (var i = 0; i < 6; i++) {
                    face(i);
                }
            }
        })();

        /*

    face:
    1 0 2
      3

    posit:
    2 8 3 7 1    0    2 8 3 7 1
      4 6 5    5 6 4    4 6 5
        0    1 7 3 8 2    0

             2 8 3 7 1
               4 6 5
                 0

         */

        var pyraImage = (function() {
            var width = 45;
            var posit = [];
            var colors = null;
            var faceoffx = [3.5, 1.5, 5.5, 3.5];
            var faceoffy = [0, 3 * hsq3, 3 * hsq3, 6.5 * hsq3];
            var g1 = [0, 6, 5, 4];
            var g2 = [1, 7, 3, 5];
            var g3 = [2, 8, 4, 3];
            var flist = [
                [0, 1, 2],
                [2, 3, 0],
                [1, 0, 3],
                [3, 2, 1]
            ];
            var arrx = [-0.5, 0.5, 0];
            var arry1 = [hsq3, hsq3, 0];
            var arry2 = [-hsq3, -hsq3, 0];

            function doMove(axis, power) {
                var len = axis >= 4 ? 1 : 4;
                var f = flist[axis % 4];
                for (var i = 0; i < len; i++) {
                    for (var p = 0; p < power; p++) {
                        mathlib.circle(posit, f[0] * 9 + g1[i], f[1] * 9 + g2[i], f[2] * 9 + g3[i]);
                    }
                }
            }

            function face(f) {

                setColors();
                colors = pyra_colors;

                var inv = f != 0;
                var arroffx = [0, -1, 1, 0, 0.5, -0.5, 0, -0.5, 0.5];
                var arroffy = [0, 2, 2, 2, 1, 1, 2, 3, 3];

                for (var i = 0; i < arroffy.length; i++) {
                    arroffy[i] *= inv ? -hsq3 : hsq3;
                    arroffx[i] *= inv ? -1 : 1;
                }
                for (var idx = 0; idx < 9; idx++) {
                    drawPolygon(ctx, colors[posit[f * 9 + idx]], [arrx, (idx >= 6 != inv) ? arry2 : arry1], [width, faceoffx[f] + arroffx[idx], faceoffy[f] + arroffy[idx]]);
                }
            }

            return function(moveseq) {
                var cnt = 0;
                for (var i = 0; i < 4; i++) {
                    for (var f = 0; f < 9; f++) {
                        posit[cnt++] = i;
                    }
                }
                var scramble = parseScramble(moveseq, 'URLB');
                for (var i = 0; i < scramble.length; i++) {
                    doMove(scramble[i][0] + (scramble[i][1] == 2 ? 4 : 0), scramble[i][2] == 1 ? 1 : 2);
                }
                var imgSize = scalingFactor / 10;
                canvas.width(7 * imgSize + 'em');
                canvas.height(6.5 * hsq3 * imgSize + 'em');

                canvas.attr('width', 7 * width);
                canvas.attr('height', 6.5 * hsq3 * width);

                for (var i = 0; i < 4; i++) {
                    face(i);
                }
            }
        })();

                /*

    face:
      3
    1 5 4 2
      0

    posit:
        0 1 2
        3 4 5
        6 7 8

         */

        var rediImage = (function() {
            var width = 30;
            var posit = [];
            var colors = null;
            var REDI_EDGE_INDICES = [1,3,5,7,10,12,14,16,19,21,23,25,28,30,32,34,37,39,41,43,46,48,50,52];

            function doMove(move) {
                if (move == 'R') {
                    mathlib.circle(posit, 35, 36, 47); // corner
                    mathlib.circle(posit, 34, 37, 50); // edges half
                    mathlib.circle(posit, 46, 32, 39); // edges half
                }
                if (move == "R'") {
                    mathlib.circle(posit, 35, 47, 36); // corner
                    mathlib.circle(posit, 34, 50, 37); // edges half
                    mathlib.circle(posit, 46, 39, 32); // edges half
                }
                if (move == 'L') {
                    mathlib.circle(posit, 33, 45, 9);  // corner
                    mathlib.circle(posit, 30, 46, 12); // edges half
                    mathlib.circle(posit, 10, 34, 48); // edges half
                }
                if (move == "L'") {
                    mathlib.circle(posit, 33, 9, 45);  // corner
                    mathlib.circle(posit, 30, 12, 46); // edges half
                    mathlib.circle(posit, 10, 48, 34); // edges half
                }
                if (move == 'x') {
                    mathlib.circle(posit, 36, 38, 44, 42); // R face corner cubelets
                    mathlib.circle(posit, 37, 41, 43, 39); // R face edge cubelets
                    mathlib.circle(posit, 9, 11, 17, 15);  // L face corner cubelets
                    mathlib.circle(posit, 10, 14, 16, 12); // L face edge cubelets
                    mathlib.circle(posit, 27, 24, 6, 45); // 'A' corner vertical line around cube
                    mathlib.circle(posit, 29, 26, 8, 47); // 'B' corner vertical line around cube
                    mathlib.circle(posit, 35, 20, 2, 53); // 'C' corner vertical line around cube
                    mathlib.circle(posit, 33, 18, 0, 51); // 'D' corner vertical line around cube
                    mathlib.circle(posit, 28, 25, 7, 46); // 'A' edge vertical line around cube
                    mathlib.circle(posit, 32, 23, 5, 50); // 'B' edge vertical line around cube
                    mathlib.circle(posit, 34, 19, 1, 52); // 'C' edge vertical line around cube
                    mathlib.circle(posit, 30, 21, 3, 48); // 'D' edge vertical line around cube
                }
            }

            function face(f) {

                size = 3;

                if (!colors) {
                    setColors();
                    colors = cube_colors;
                }

                var offx = 10 / 9,
                    offy = 10 / 9;
                if (f == 0) { //D
                    offx *= size;
                    offy *= size * 2;
                } else if (f == 1) { //L
                    offx *= 0;
                    offy *= size;
                } else if (f == 2) { //B
                    offx *= size * 3;
                    offy *= size;
                } else if (f == 3) { //U
                    offx *= size;
                    offy *= 0;
                } else if (f == 4) { //R
                    offx *= size * 2;
                    offy *= size;
                } else if (f == 5) { //F
                    offx *= size;
                    offy *= size;
                }

                for (var i = 0; i < size; i++) {
                    var x = (f == 1 || f == 2) ? size - 1 - i : i;
                    for (var j = 0; j < size; j++) {
                        var y = (f == 0) ? size - 1 - j : j;
                        if ((i == 1) && (j == 1)) { continue; }

                        var posit_index = (f * size + y) * size + x;
                        var color = colors[posit[posit_index]];

                        if (REDI_EDGE_INDICES.includes(posit_index)) {
                            if (i == 0 && j == 1) {
                                drawPolygon(ctx, color, [
                                    [i, i,     i + 1, i + 1.5, i + 1],
                                    [j, j + 1, j + 1, j + 0.5, j]
                                ], [width, offx, offy]);
                            } else if (i == 1 && j == 0) {
                                drawPolygon(ctx, color, [
                                    [i, i,     i + 0.5, i + 1, i + 1],
                                    [j, j + 1, j + 1.5, j + 1, j]
                                ], [width, offx, offy]);
                            } else if (i == 2 && j == 1) {
                                drawPolygon(ctx, color, [
                                    [i, i - 0.5, i,     i + 1, i + 1],
                                    [j, j + 0.5, j + 1, j + 1, j]
                                ], [width, offx, offy]);
                            } else {
                                drawPolygon(ctx, color, [
                                    [i, i,     i + 1, i + 1, i + 0.5],
                                    [j, j + 1, j + 1, j    , j - 0.5]
                                ], [width, offx, offy]);
                            }
                        } else {
                            drawPolygon(ctx, color, [
                                [i, i, i + 1, i + 1],
                                [j, j + 1, j + 1, j]
                            ], [width, offx, offy]);
                        }
                    }
                }
            }

            return function(moveseq) {
                var cnt = 0;
                for (var i = 0; i < 6; i++) {
                    for (var f = 0; f < 9; f++) {
                        posit[cnt++] = i;
                    }
                }

                var scramble = moveseq.split(' ');
                for (var i = 0; i < scramble.length; i++) {
                    doMove(scramble[i]);
                }

                var imgSize = scalingFactor / 50;
                canvas.width(39 * imgSize + 'em');
                canvas.height(29 * imgSize + 'em');

                canvas.attr('width', 39 * 3 / 9 * width + 1);
                canvas.attr('height', 29 * 3 / 9 * width + 1);

                for (var i = 0; i < 6; i++) {
                    face(i);
                }
            }
        })();

        var dinoImage = (function() {
            var width = 30;
            var posit = [];
            var colors = null;
            var DINO_EDGE_INDICES = [1,3,5,7,10,12,14,16,19,21,23,25,28,30,32,34,37,39,41,43,46,48,50,52];

            function doMove(move) {
                if (move == 'R') {
                    mathlib.circle(posit, 34, 37, 50); // edges half
                    mathlib.circle(posit, 46, 32, 39); // edges half
                }
                if (move == "R'") {
                    mathlib.circle(posit, 34, 50, 37); // edges half
                    mathlib.circle(posit, 46, 39, 32); // edges half
                }
                if (move == 'L') {
                    mathlib.circle(posit, 30, 46, 12); // edges half
                    mathlib.circle(posit, 10, 34, 48); // edges half
                }
                if (move == "L'") {
                    mathlib.circle(posit, 30, 12, 46); // edges half
                    mathlib.circle(posit, 10, 48, 34); // edges half
                }
                if (move == 'x') {
                    mathlib.circle(posit, 37, 41, 43, 39); // R face edge cubelets
                    mathlib.circle(posit, 10, 14, 16, 12); // L face edge cubelets
                    mathlib.circle(posit, 28, 25, 7, 46); // 'A' edge vertical line around cube
                    mathlib.circle(posit, 32, 23, 5, 50); // 'B' edge vertical line around cube
                    mathlib.circle(posit, 34, 19, 1, 52); // 'C' edge vertical line around cube
                    mathlib.circle(posit, 30, 21, 3, 48); // 'D' edge vertical line around cube
                }
            }

            function face(f) {

                size = 3;

                if (!colors) {
                    setColors();
                    colors = cube_colors;
                }

                var offx = 10 / 9,
                    offy = 10 / 9;
                if (f == 0) { //D
                    offx *= size;
                    offy *= size * 2;
                } else if (f == 1) { //L
                    offx *= 0;
                    offy *= size;
                } else if (f == 2) { //B
                    offx *= size * 3;
                    offy *= size;
                } else if (f == 3) { //U
                    offx *= size;
                    offy *= 0;
                } else if (f == 4) { //R
                    offx *= size * 2;
                    offy *= size;
                } else if (f == 5) { //F
                    offx *= size;
                    offy *= size;
                }

                for (var i = 0; i < size; i++) {
                    var x = (f == 1 || f == 2) ? size - 1 - i : i;
                    for (var j = 0; j < size; j++) {
                        var y = (f == 0) ? size - 1 - j : j;
                        if ((i == 1) && (j == 1)) { continue; }

                        var posit_index = (f * size + y) * size + x;
                        var color = colors[posit[posit_index]];

                        if (DINO_EDGE_INDICES.includes(posit_index)) {
                            if (i == 0 && j == 1) {
                                drawPolygon(ctx, color, [
                                    [i,     i + 1.5, i],
                                    [j - 1, j + 0.5, j + 2]
                                ], [width, offx, offy]);
                            } else if (i == 1 && j == 0) {
                                drawPolygon(ctx, color, [
                                    [i - 1, i + 0.5, i + 2],
                                    [j,     j + 1.5, j]
                                ], [width, offx, offy]);
                            } else if (i == 2 && j == 1) {
                                drawPolygon(ctx, color, [
                                    [i + 1 , i + 1 , i - 0.5],
                                    [j - 1 , j + 2 , j + 0.5]
                                ], [width, offx, offy]);
                            } else {
                                drawPolygon(ctx, color, [
                                    [i + 0.5, i + 2, i - 1],
                                    [j - 0.5, j + 1, j + 1]
                                ], [width, offx, offy]);
                            }
                        }
                    }
                }
            }

            return function(moveseq) {
                var cnt = 0;
                for (var i = 0; i < 6; i++) {
                    for (var f = 0; f < 9; f++) {
                        posit[cnt++] = i;
                    }
                }

                var scramble = moveseq.split(' ');
                for (var i = 0; i < scramble.length; i++) {
                    doMove(scramble[i]);
                }

                var imgSize = scalingFactor / 50;
                canvas.width(39 * imgSize + 'em');
                canvas.height(29 * imgSize + 'em');

                canvas.attr('width', 39 * 3 / 9 * width + 1);
                canvas.attr('height', 29 * 3 / 9 * width + 1);

                for (var i = 0; i < 6; i++) {
                    face(i);
                }
            }
        })();

        var fifteenImage = (function() {
            var posit = [];
            var empty_ix = null;

            function doMove(move) {
                if (move == 'L') {
                    mathlib.circle(posit, empty_ix, empty_ix + 1);
                    empty_ix = empty_ix + 1;
                }
                if (move == 'R') {
                    mathlib.circle(posit, empty_ix, empty_ix - 1);
                    empty_ix = empty_ix - 1;
                }
                if (move == 'U') {
                    mathlib.circle(posit, empty_ix, empty_ix + 4);
                    empty_ix = empty_ix + 4;
                }
                if (move == 'D') {
                    mathlib.circle(posit, empty_ix, empty_ix - 4);
                    empty_ix = empty_ix - 4;
                }
            }

            function renderNumber(width, x, y, value) {
                ctx.fillStyle = "#000";
                ctx.font = "50px Calibri";
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillText(value, width * x, width * y);
            }

            function render() {

                var width = 110;
                var offset = 1.05;

                var cream = '#d1d1b4';
                var red = '#b5382f';

                var colors = {
                    1: red,
                    3: red,
                    6: red,
                    8: red,
                    9: red,
                    11: red,
                    14: red,

                    2: cream,
                    4: cream,
                    5: cream,
                    7: cream,
                    10: cream,
                    12: cream,
                    13: cream,
                    15: cream,
                };

                // I'm aware this is terrible and not abstracted, no need to tell me

                // row 1
                if (empty_ix != 0) {
                    drawPolygon(ctx, colors[posit[0]], [[0, 1, 1, 0], [0, 0, 1, 1]], [width, 0, 0]);
                    renderNumber(width, 0.5, 0.5, posit[0]);
                }

                if (empty_ix != 1) {
                    drawPolygon(ctx, colors[posit[1]], [[0, 1, 1, 0], [0, 0, 1, 1]], [width, 1*offset, 0]);
                    renderNumber(width, offset*1.5, 0.5, posit[1]);
                }

                if (empty_ix != 2) {
                    drawPolygon(ctx, colors[posit[2]], [[0, 1, 1, 0], [0, 0, 1, 1]], [width, 2*offset, 0]);
                    renderNumber(width, offset*2.5, 0.5, posit[2]);
                }

                if (empty_ix != 3) {
                    drawPolygon(ctx, colors[posit[3]], [[0, 1, 1, 0], [0, 0, 1, 1]], [width, 3*offset, 0]);
                    renderNumber(width, offset*3.5, 0.5, posit[3]);
                }

                // row 2
                if (empty_ix != 4) {
                    drawPolygon(ctx, colors[posit[4]], [[0, 1, 1, 0], [0, 0, 1, 1]], [width, 0, 1*offset]);
                    renderNumber(width, 0.5, offset*1.5, posit[4]);
                }

                if (empty_ix != 5) {
                    drawPolygon(ctx, colors[posit[5]], [[0, 1, 1, 0], [0, 0, 1, 1]], [width, 1*offset, 1*offset]);
                    renderNumber(width, offset*1.5, offset*1.5, posit[5]);
                }

                if (empty_ix != 6) {
                    drawPolygon(ctx, colors[posit[6]], [[0, 1, 1, 0], [0, 0, 1, 1]], [width, 2*offset, 1*offset]);
                    renderNumber(width, offset*2.5, offset*1.5, posit[6]);
                }

                if (empty_ix != 7) {
                    drawPolygon(ctx, colors[posit[7]], [[0, 1, 1, 0], [0, 0, 1, 1]], [width, 3*offset, 1*offset]);
                    renderNumber(width, offset*3.5, offset*1.5, posit[7]);
                }

                // row 3
                if (empty_ix != 8) {
                    drawPolygon(ctx, colors[posit[8]], [[0, 1, 1, 0], [0, 0, 1, 1]], [width, 0, 2*offset]);
                    renderNumber(width, 0.5, offset*2.5, posit[8]);
                }

                if (empty_ix != 9) {
                    drawPolygon(ctx, colors[posit[9]], [[0, 1, 1, 0], [0, 0, 1, 1]], [width, 1*offset, 2*offset]);
                    renderNumber(width, offset*1.5, offset*2.5, posit[9]);
                }

                if (empty_ix != 10) {
                    drawPolygon(ctx, colors[posit[10]], [[0, 1, 1, 0], [0, 0, 1, 1]], [width, 2*offset, 2*offset]);
                    renderNumber(width, offset*2.5, offset*2.5, posit[10]);
                }

                if (empty_ix != 11) {
                    drawPolygon(ctx, colors[posit[11]], [[0, 1, 1, 0], [0, 0, 1, 1]], [width, 3*offset, 2*offset]);
                    renderNumber(width, offset*3.5, offset*2.5, posit[11]);
                }

                // row 4
                if (empty_ix != 12) {
                    drawPolygon(ctx, colors[posit[12]], [[0, 1, 1, 0], [0, 0, 1, 1]], [width, 0, 3*offset]);
                    renderNumber(width, 0.5, offset*3.5, posit[12]);
                }

                if (empty_ix != 13) {
                    drawPolygon(ctx, colors[posit[13]], [[0, 1, 1, 0], [0, 0, 1, 1]], [width, 1*offset, 3*offset]);
                    renderNumber(width, offset*1.5, offset*3.5, posit[13]);
                }

                if (empty_ix != 14) {
                    drawPolygon(ctx, colors[posit[14]], [[0, 1, 1, 0], [0, 0, 1, 1]], [width, 2*offset, 3*offset]);
                    renderNumber(width, offset*2.5, offset*3.5, posit[14]);
                }

                if (empty_ix != 15) {
                    drawPolygon(ctx, colors[posit[15]], [[0, 1, 1, 0], [0, 0, 1, 1]], [width, 3*offset, 3*offset]);
                    renderNumber(width, offset*3.5, offset*3.5, posit[15]);
                }
            }

            return function(moveseq) {
                empty_ix = 15;

                var cnt = 0;
                for (var i = 0; i < 15; i++) {
                    posit[cnt++] = i+1;
                }
                posit[15] = '';

                var scramble = moveseq.split(' ');
                for (var i = 0; i < scramble.length; i++) {
                    var move_candidate = scramble[i];
                    if (move_candidate.length == 1) {
                        doMove(move_candidate);
                    } else {
                        var move = move_candidate[0];
                        var num  = parseInt(move_candidate[1]);
                        for(var j = 0; j < num; j++) {
                            doMove(move);
                        }
                    }
                }

                var what1 = 25;
                var what2 = 25;
                var width = 20;

                var imgSize = scalingFactor / 50;
                canvas.width(what1 * imgSize + 'em');
                canvas.height(what2 * imgSize + 'em');

                canvas.attr('width', what1 * width + 1);
                canvas.attr('height', what2 * width + 1);

                render();
            }
        })();

        var ftoImage = (function() {
            var posit = [];
            var colors = null;

            function doMove(move) {
                if (move == 'U') {
                    var stripL = [9, 10, 14, 15, 17];  // L face strip shared with U
                    var stripB = [36, 37, 38, 39, 40]; // B face strip shared with U
                    var stripR = [27, 29, 28, 32, 31]; // R face strip shared with U

                    for (var i = 0; i < 5; i++) {
                        mathlib.circle(posit, stripL[i], stripB[i], stripR[i]);
                    }

                    mathlib.circle(posit, 18, 67, 45); // Shared-colors corner triangles
                    mathlib.circle(posit, 0, 4, 8);    // Face corners
                    mathlib.circle(posit, 1, 3, 6);    // Face centers
                    mathlib.circle(posit, 2, 7, 5);    // Face edges
                }

                if (move == 'L') {
                    var stripU  = [0, 1, 5, 6, 8];      // U face strip shared with L
                    var stripF  = [18, 20, 19, 23, 22]; // F face strip shared with L
                    var stripBL = [71, 70, 69, 68, 67]; // BL face strip shared with L

                    for (var i = 0; i < 5; i++) {
                        mathlib.circle(posit, stripU[i], stripF[i], stripBL[i]);
                    }

                    mathlib.circle(posit, 27, 62, 40); // Shared-colors corner triangles
                    mathlib.circle(posit, 9, 17, 13);  // Face corners
                    mathlib.circle(posit, 10, 15, 12); // Face centers
                    mathlib.circle(posit, 14, 16, 11); // Face edges
                }

                if (move == 'R') {
                    var stripU  = [8, 6, 7, 3, 4];      // U face strip shared with R
                    var stripBR = [45, 46, 47, 48, 49]; // BR face strip shared with R
                    var stripF  = [26, 25, 21, 20, 18]; // F face strip shared with R

                    for (var i = 0; i < 5; i++) {
                        mathlib.circle(posit, stripU[i], stripBR[i], stripF[i]);
                    }

                    mathlib.circle(posit, 17, 36, 58); // Shared-colors corner triangles
                    mathlib.circle(posit, 27, 31, 35);  // Face corners
                    mathlib.circle(posit, 29, 32, 34); // Face centers
                    mathlib.circle(posit, 28, 33, 30); // Face edges
                }

                if (move == 'F') {
                    var stripR = [27, 29, 30, 34, 35]; // R face strip shared with F
                    var stripD = [58, 59, 60, 61, 62]; // D face strip shared with F
                    var stripL = [13, 12, 16, 15, 17]; // L face strip shared with F

                    for (var i = 0; i < 5; i++) {
                        mathlib.circle(posit, stripR[i], stripD[i], stripL[i]);
                    }

                    mathlib.circle(posit, 8, 49, 71);  // Shared-colors corner triangles
                    mathlib.circle(posit, 18, 26, 22); // Face corners
                    mathlib.circle(posit, 20, 25, 23); // Face centers
                    mathlib.circle(posit, 19, 21, 24); // Face edges
                }

                if (move == 'B') {
                    var stripU  = [4, 3, 2, 1, 0];      // U face strip shared with B
                    var stripBL = [67, 68, 64, 65, 63]; // BL face strip shared with B
                    var stripBR = [53, 51, 50, 46, 45]; // BR face strip shared with B

                    for (var i = 0; i < 5; i++) {
                        mathlib.circle(posit, stripU[i], stripBL[i], stripBR[i]);
                    }

                    mathlib.circle(posit, 54, 31, 9);  // Shared-colors corner triangles
                    mathlib.circle(posit, 36, 40, 44); // Face corners
                    mathlib.circle(posit, 37, 39, 42); // Face centers
                    mathlib.circle(posit, 38, 43, 41); // Face edges
                }

                if (move == 'BR') {
                    var stripB = [36, 37, 41, 42, 44]; // B face strip shared with BR
                    var stripD = [54, 56, 55, 59, 58]; // D face strip shared with BR
                    var stripR = [35, 34, 33, 32, 31]; // R face strip shared with BR

                    for (var i = 0; i < 5; i++) {
                        mathlib.circle(posit, stripB[i], stripD[i], stripR[i]);
                    }

                    mathlib.circle(posit, 63, 26, 4);  // Shared-colors corner triangles
                    mathlib.circle(posit, 45, 53, 49); // Face corners
                    mathlib.circle(posit, 46, 51, 48); // Face centers
                    mathlib.circle(posit, 50, 52, 47); // Face edges
                }

                if (move == 'BL') {
                    var stripB = [44, 42, 43, 39, 40]; // B face strip shared with BL
                    var stripL = [9, 10, 11, 12, 13];  // L face strip shared with BL
                    var stripD = [62, 61, 57, 56, 54]; // D face strip shared with BL

                    for (var i = 0; i < 5; i++) {
                        mathlib.circle(posit, stripB[i], stripL[i], stripD[i]);
                    }

                    mathlib.circle(posit, 53, 0, 22);  // Shared-colors corner triangles
                    mathlib.circle(posit, 63, 67, 71); // Face corners
                    mathlib.circle(posit, 65, 68, 70); // Face centers
                    mathlib.circle(posit, 64, 69, 66); // Face edges
                }

                if (move == 'D') {
                    var stripBR = [49, 48, 52, 51, 53]; // BR face strip shared with D
                    var stripBL = [63, 65, 66, 70, 71];  // BL face strip shared with D
                    var stripF = [22, 23, 24, 25, 26];  // F face strip shared with D

                    for (var i = 0; i < 5; i++) {
                        mathlib.circle(posit, stripBR[i], stripBL[i], stripF[i]);
                    }

                    mathlib.circle(posit, 44, 13, 35);  // Shared-colors corner triangles
                    mathlib.circle(posit, 54, 62, 58); // Face corners
                    mathlib.circle(posit, 56, 61, 59); // Face centers
                    mathlib.circle(posit, 55, 57, 60); // Face edges
                }
            }

            function renderChar(width, x, y, value) {
                ctx.fillStyle = "#000";
                ctx.font = "25px Calibri";
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillText(value, width * x, width * y);
            }

            function drawHeavyLine(x1, y1, x2, y2, scale) {
                ctx.beginPath();
                ctx.moveTo(x1*scale, y1*scale);
                ctx.lineTo(x2*scale, y2*scale);
                ctx.lineWidth = 3;
                ctx.stroke();
                ctx.lineWidth = 1;
            }

            function render() {
                var width = 250;
                var fraction = width/6;

                setColors();
                colors = fto_colors;

                var half_coords = {
                    // U (or B with +36)
                    1: [[0, 2, 1], [0, 0, 1]],
                    2: [[2, 3, 1], [0, 1, 1]],
                    3: [[2, 4, 3], [0, 0, 1]],
                    4: [[4, 5, 3], [0, 1, 1]],
                    5: [[4, 6, 5], [0, 0, 1]],
                    6: [[1, 3, 2], [1, 1, 2]],
                    7: [[3, 4, 2], [1, 2, 2]],
                    8: [[3, 5, 4], [1, 1, 2]],
                    9: [[2, 4, 3], [2, 2, 3]],

                    // L (or BR with +36)
                    10: [[0, 1, 0], [0, 1, 2]],
                    11: [[0, 1, 1], [2, 1, 3]],
                    12: [[0, 1, 0], [2, 3, 4]],
                    13: [[0, 1, 1], [4, 3, 5]],
                    14: [[0, 1, 0], [4, 5, 6]],
                    15: [[1, 2, 1], [1, 2, 3]],
                    16: [[1, 2, 2], [3, 2, 4]],
                    17: [[1, 2, 1], [3, 4, 5]],
                    18: [[2, 3, 2], [2, 3, 4]],

                    // F (or D with +36)
                    19: [[2, 3, 4], [4, 3, 4]],
                    20: [[1, 2, 3], [5, 4, 5]],
                    21: [[2, 4, 3], [4, 4, 5]],
                    22: [[3, 4, 5], [5, 4, 5]],
                    23: [[0, 1, 2], [6, 5, 6]],
                    24: [[1, 3, 2], [5, 5, 6]],
                    25: [[2, 3, 4], [6, 5, 6]],
                    26: [[3, 5, 4], [5, 5, 6]],
                    27: [[4, 5, 6], [6, 5, 6]],

                    // R (or BL with +36)
                    28: [[3, 4, 4], [3, 2, 4]],
                    29: [[4, 5, 5], [2, 1, 3]],
                    30: [[4, 5, 4], [2, 3, 4]],
                    31: [[4, 5, 5], [4, 3, 5]],
                    32: [[5, 6, 6], [1, 0, 2]],
                    33: [[5, 6, 5], [1, 2, 3]],
                    34: [[5, 6, 6], [3, 2, 4]],
                    35: [[5, 6, 5], [3, 4, 5]],
                    36: [[5, 6, 6], [5, 4, 6]],
                }

                for (var i = 1; i < 37; i++) {
                    var coords = half_coords[i];
                    var x = coords[0];
                    var y = coords[1];
                    var shifted = [[x[0], x[1], x[2]], [y[0]+3, y[1]+3, y[2]+3]];

                    drawPolygon(ctx, colors[posit[i-1]], shifted, [fraction, 0, 0]);

                    // var lx = (Math.min(...shifted[0]) + Math.max(...shifted[0])) / 2;
                    // var ly = (Math.min(...shifted[1]) + Math.max(...shifted[1])) / 2;
                    // renderChar(fraction, lx, ly, i-1);
                }
                // drawHeavyLine(0, 3, 6, 9, fraction);
                // drawHeavyLine(6, 3, 0, 9, fraction);

                
                for (var i = 37; i < 73; i++) {
                    var coords = half_coords[i-36];
                    var x = coords[0];
                    var y = coords[1];
                    var shifted = [[x[0]+6, x[1]+6, x[2]+6], [y[0]+3, y[1]+3, y[2]+3]];

                    drawPolygon(ctx, colors[posit[i-1]], shifted, [fraction, 0, 0]);

                    // var lx = (Math.min(...shifted[0]) + Math.max(...shifted[0])) / 2;
                    // var ly = (Math.min(...shifted[1]) + Math.max(...shifted[1])) / 2;
                    // renderChar(fraction, lx, ly, i-1);
                }
                // drawHeavyLine(6, 3, 12, 9, fraction);
                // drawHeavyLine(12, 3, 6, 9, fraction);

                drawHeavyLine(2, 0, 4, 2, fraction);
                drawHeavyLine(4, 0, 2, 2, fraction);
                renderChar(fraction, 3, 0.3, "U");
                renderChar(fraction, 3.75, 1, "R");
                renderChar(fraction, 3, 1.7, "F");
                renderChar(fraction, 2.25, 1, "L");

                drawHeavyLine(8, 0, 10, 2, fraction);
                drawHeavyLine(8, 2, 10, 0, fraction);
                renderChar(fraction, 9, 0.3, "B");
                renderChar(fraction, 9.75, 1, "BL");
                renderChar(fraction, 9, 1.7, "D");
                renderChar(fraction, 8.25, 1, "BR");
            }

            return function(moveseq) {
                var cnt = 0;
                var faceSize = 9;
                for (var i = 0; i < 8; i++) {
                    for (var f = 0; f < faceSize; f++) {
                        posit[cnt++] = i;
                    }
                }

                var scramble = moveseq.split(' ');
                for (var i = 0; i < scramble.length; i++) {
                    var move = scramble[i];
                    if (move.endsWith("'")) {
                        move = move.replace("'", "");
                        // U' == U U
                        doMove(move);
                        doMove(move);
                    } else {
                        doMove(move);
                    }
                }

                var what1 = 25;
                var what2 = 20;
                var width = 20;

                var imgSize = scalingFactor / 50;
                canvas.width(what1 * imgSize + 'em');
                canvas.height(what2 * imgSize + 'em');

                canvas.attr('width', what1 * width + 1);
                canvas.attr('height', what2 * width + 1);

                render();
            }
        })();

        var image334 = (function() {
            var width = 24;
            var posit = [];
            var colors = null;

            function doMove(move) {
                if (move == 'M2') {
                    mathlib.circle(posit, 37, 4); // U -> D center
                    mathlib.circle(posit, 36, 3); // U -> D edges top
                    mathlib.circle(posit, 38, 5); // U -> D edges bottom
                    mathlib.circle(posit, 58, 28); // F -> B top
                    mathlib.circle(posit, 59, 27); // F -> B top edges
                    mathlib.circle(posit, 60, 26); // F -> B bottom edges
                    mathlib.circle(posit, 61, 25); // F -> B bottom
                }
                if (move == 'S2') {
                    mathlib.circle(posit, 37, 4); // U -> D center
                    mathlib.circle(posit, 34, 7); // U -> D edges left
                    mathlib.circle(posit, 40, 1); // U -> D edges right
                    mathlib.circle(posit, 13, 49); // L -> R top
                    mathlib.circle(posit, 14, 48); // L -> R top edges
                    mathlib.circle(posit, 15, 47); // L -> R bottom edges
                    mathlib.circle(posit, 16, 46); // L -> R bottom
                    
                }
                if (move == 'U') {
                    mathlib.circle(posit, 36, 40, 38, 34); // U edges
                    mathlib.circle(posit, 33, 39, 41, 35); // U corners
                    mathlib.circle(posit, 13, 25, 46, 58); // U-adjacent edges
                    mathlib.circle(posit, 9, 21, 42, 54); // U-adjacent left corners
                    mathlib.circle(posit, 17, 29, 50, 62); // U-adjacent right corners
                }
                if (move == 'U2') {
                    for (var v = 0; v < 2; v++) {
                        mathlib.circle(posit, 36, 40, 38, 34); // U edges
                        mathlib.circle(posit, 33, 39, 41, 35); // U corners
                        mathlib.circle(posit, 13, 25, 46, 58); // U-adjacent edges
                        mathlib.circle(posit, 9, 21, 42, 54); // U-adjacent left corners
                        mathlib.circle(posit, 17, 29, 50, 62); // U-adjacent right corners
                    }
                }
                if (move == "U'") {
                    for (var v = 0; v < 3; v++) {
                        mathlib.circle(posit, 36, 40, 38, 34); // U edges
                        mathlib.circle(posit, 33, 39, 41, 35); // U corners
                        mathlib.circle(posit, 13, 25, 46, 58); // U-adjacent edges
                        mathlib.circle(posit, 9, 21, 42, 54); // U-adjacent left corners
                        mathlib.circle(posit, 17, 29, 50, 62); // U-adjacent right corners
                    }
                }
                if (move == 'u') {
                    mathlib.circle(posit, 59, 14, 26, 47); // u centers
                    mathlib.circle(posit, 55, 10, 22, 43); // u left edges
                    mathlib.circle(posit, 63, 18, 30, 51); // u right edges
                }
                if (move == 'u2') {
                    for (var v = 0; v < 2; v++) {
                        mathlib.circle(posit, 59, 14, 26, 47); // u centers
                        mathlib.circle(posit, 55, 10, 22, 43); // u left edges
                        mathlib.circle(posit, 63, 18, 30, 51); // u right edges
                    }
                }
                if (move == "u'") {
                    for (var v = 0; v < 3; v++) {
                        mathlib.circle(posit, 59, 14, 26, 47); // u centers
                        mathlib.circle(posit, 55, 10, 22, 43); // u left edges
                        mathlib.circle(posit, 63, 18, 30, 51); // u right edges
                    }
                }
                if (move == 'D') {
                    mathlib.circle(posit, 3, 7, 5, 1); // D edges
                    mathlib.circle(posit, 0, 6, 8, 2); // D corners
                    mathlib.circle(posit, 61, 49, 28, 16); // D-adjacent edges
                    mathlib.circle(posit, 57, 45, 24, 12); // D-adjacent left corners
                    mathlib.circle(posit, 65, 53, 32, 20); // D-adjacent right corners
                }
                if (move == 'D2') {
                    for (var v = 0; v < 2; v++) {
                        mathlib.circle(posit, 3, 7, 5, 1); // D edges
                        mathlib.circle(posit, 0, 6, 8, 2); // D corners
                        mathlib.circle(posit, 61, 49, 28, 16); // D-adjacent edges
                        mathlib.circle(posit, 57, 45, 24, 12); // D-adjacent left corners
                        mathlib.circle(posit, 65, 53, 32, 20); // D-adjacent right corners
                    }
                }
                if (move == "D'") {
                    for (var v = 0; v < 3; v++) {
                        mathlib.circle(posit, 3, 7, 5, 1); // D edges
                        mathlib.circle(posit, 0, 6, 8, 2); // D corners
                        mathlib.circle(posit, 61, 49, 28, 16); // D-adjacent edges
                        mathlib.circle(posit, 57, 45, 24, 12); // D-adjacent left corners
                        mathlib.circle(posit, 65, 53, 32, 20); // D-adjacent right corners
                    }
                }
                if (move == 'R2') {
                    mathlib.circle(posit, 40, 7); // U -> D edges
                    mathlib.circle(posit, 39, 6); // U -> D corners top
                    mathlib.circle(posit, 41, 8); // U -> D corners bottom
                    mathlib.circle(posit, 62, 24); // F -> B top corners
                    mathlib.circle(posit, 65, 21); // F -> B bottom corners
                    mathlib.circle(posit, 63, 23); // F -> B top edges
                    mathlib.circle(posit, 64, 22); // F -> B bottom edges
                    mathlib.circle(posit, 42, 53); // R corners top-left to bottom-right
                    mathlib.circle(posit, 50, 45); // R corners top-right to bottom-left
                    mathlib.circle(posit, 46, 49); // R top/bottom edges
                    mathlib.circle(posit, 43, 52); // R edges #1
                    mathlib.circle(posit, 51, 44); // R edges #2
                    mathlib.circle(posit, 47, 48); // R centers
                }
                if (move == 'L2') {
                    mathlib.circle(posit, 34, 1); // U -> D edges
                    mathlib.circle(posit, 33, 0); // U -> D corners top
                    mathlib.circle(posit, 35, 2); // U -> D corners bottom
                    mathlib.circle(posit, 54, 32); // F -> B top corners
                    mathlib.circle(posit, 57, 29); // F -> B bottom corners
                    mathlib.circle(posit, 55, 31); // F -> B top edges
                    mathlib.circle(posit, 56, 30); // F -> B bottom edges
                    mathlib.circle(posit, 9, 20); // L corners top-left to bottom-right
                    mathlib.circle(posit, 17, 12); // L corners top-right to bottom-left
                    mathlib.circle(posit, 13, 16); // L top/bottom edges
                    mathlib.circle(posit, 10, 19); // L edges #1
                    mathlib.circle(posit, 11, 18); // L edges #2
                    mathlib.circle(posit, 14, 15); // L centers
                }
                if (move == 'F2') {
                    mathlib.circle(posit, 38, 3); // U -> D edges
                    mathlib.circle(posit, 35, 6); // U -> D corners left
                    mathlib.circle(posit, 41, 0); // U -> D corners right
                    mathlib.circle(posit, 17, 45); // L -> R top corners
                    mathlib.circle(posit, 20, 42); // L -> R bottom corners
                    mathlib.circle(posit, 18, 44); // L -> R top edges
                    mathlib.circle(posit, 19, 43); // L -> R bottom edges
                    mathlib.circle(posit, 54, 65); // F corners top-left to bottom-right
                    mathlib.circle(posit, 57, 62); // F corners top-right to bottom-left
                    mathlib.circle(posit, 58, 61); // F top/bottom edges
                    mathlib.circle(posit, 55, 64); // F edges #1
                    mathlib.circle(posit, 56, 63); // F edges #2
                    mathlib.circle(posit, 59, 60); // F centers
                }
                if (move == 'B2') {
                    mathlib.circle(posit, 36, 5); // U -> D edges
                    mathlib.circle(posit, 33, 8); // U -> D corners left
                    mathlib.circle(posit, 39, 2); // U -> D corners right
                    mathlib.circle(posit, 9, 53); // L -> R top corners
                    mathlib.circle(posit, 12, 50); // L -> R bottom corners
                    mathlib.circle(posit, 10, 52); // L -> R top edges
                    mathlib.circle(posit, 11, 51); // L -> R bottom edges
                    mathlib.circle(posit, 21, 32); // B corners top-left to bottom-right
                    mathlib.circle(posit, 29, 24); // B corners top-right to bottom-left
                    mathlib.circle(posit, 25, 28); // B top/bottom edges
                    mathlib.circle(posit, 22, 31); // B edges #1
                    mathlib.circle(posit, 23, 30); // B edges #2
                    mathlib.circle(posit, 26, 27); // B centers
                }
            }

            function face(f) {

                size = 3;
                longSize = 4;

                if (!colors) {
                    setColors();
                    colors = cube_colors;
                }

                var offx = 10 / 9,
                    offy = 10 / 9;
                if (f == 0) { //D
                    offx *= size;
                    offy *= size * 2.33;
                } else if (f == 1) { //L
                    offx *= 0;
                    offy *= size;
                } else if (f == 2) { //B
                    offx *= size * 3;
                    offy *= size;
                } else if (f == 3) { //U
                    offx *= size;
                    offy *= 0;
                } else if (f == 4) { //R
                    offx *= size * 2;
                    offy *= size;
                } else if (f == 5) { //F
                    offx *= size;
                    offy *= size;
                }

                var topOffset = 1;
                offy += topOffset;

                if (f == 3 || f == 0) {

                    var cnt = 0;
                    if (f == 3) {
                        cnt = 33;
                    } else {
                        cnt = 0;
                    }

                    for (var i = 0; i < size; i++) {
                        for (var j = 0; j < size; j++) {
                            drawPolygon(ctx, colors[posit[cnt]], [
                                [i, i, i + 1, i + 1],
                                [j, j + 1, j + 1, j]
                            ], [width, offx, offy]);
                            cnt += 1;
                        }
                    }
                } else {

                    var cnt = 0;
                    if (f == 1) {
                        cnt = 9;
                    } else if (f == 5) {
                        cnt = 54;
                    } else if (f == 4) {
                        cnt = 42;
                    } else {
                        cnt = 21;
                    }

                    for (var i = 0; i < size; i++) {
                        for (var j = 0; j < longSize; j++) {
                            drawPolygon(ctx, colors[posit[cnt]], [
                                [i, i, i + 1, i + 1],
                                [j, j + 1, j + 1, j]
                            ], [width, offx, offy]);
                            cnt += 1;
                        }
                    }
                }
            }

            return function(moveseq) {
                var cnt = 0;
                for (var i = 0; i < 6; i++) {
                    var faceSize = (i == 3 || i == 0) ? 9 : 12;
                    for (var f = 0; f < faceSize; f++) {
                        posit[cnt++] = i;
                    }
                }

                var scramble = moveseq.split(' ');
                for (var i = 0; i < scramble.length; i++) {
                    doMove(scramble[i]);
                }

                var imgSize = scalingFactor / 50;
                canvas.width(39 * imgSize + 'em');
                canvas.height((29 * imgSize)*1.33 + 'em');

                canvas.attr('width', 39 * 3 / 9 * width + 1);
                canvas.attr('height', 29 * 4 / 9 * width + 1);

                for (var i = 0; i < 6; i++) {
                    face(i);
                }
            }
        })();

        var image223 = (function() {
            var width = 30;
            var posit = [];
            var colors = null;

            function doMove(move) {
                if (move == 'U') {
                    mathlib.circle(posit, 16, 18, 19, 17); // U corners
                    mathlib.circle(posit, 26, 4, 10, 20); // U-adjacent left corners
                    mathlib.circle(posit, 29, 7, 13, 23); // U-adjacent right corners
                }
                if (move == 'U2') {
                    for (var v = 0; v < 2; v++) {
                        mathlib.circle(posit, 16, 18, 19, 17); // U corners
                        mathlib.circle(posit, 26, 4, 10, 20); // U-adjacent left corners
                        mathlib.circle(posit, 29, 7, 13, 23); // U-adjacent right corners
                    }
                }
                if (move == "U'") {
                    for (var v = 0; v < 3; v++) {
                        mathlib.circle(posit, 16, 18, 19, 17); // U corners
                        mathlib.circle(posit, 26, 4, 10, 20); // U-adjacent left corners
                        mathlib.circle(posit, 29, 7, 13, 23); // U-adjacent right corners
                    }
                }
                if (move == 'D') {
                    mathlib.circle(posit, 0, 2, 3, 1); // D corners
                    mathlib.circle(posit, 28, 22, 12, 6); // D-adjacent left corners
                    mathlib.circle(posit, 31, 25, 15, 9); // D-adjacent right corners
                }
                if (move == 'D2') {
                    for (var v = 0; v < 2; v++) {
                        mathlib.circle(posit, 0, 2, 3, 1); // D corners
                        mathlib.circle(posit, 28, 22, 12, 6); // D-adjacent left corners
                        mathlib.circle(posit, 31, 25, 15, 9); // D-adjacent right corners
                    }
                }
                if (move == "D'") {
                    for (var v = 0; v < 3; v++) {
                        mathlib.circle(posit, 0, 2, 3, 1); // D corners
                        mathlib.circle(posit, 28, 22, 12, 6); // D-adjacent left corners
                        mathlib.circle(posit, 31, 25, 15, 9); // D-adjacent right corners
                    }
                }
                if (move == 'R2') {
                    mathlib.circle(posit, 18, 2); // U -> D corners top
                    mathlib.circle(posit, 19, 3); // U -> D corners bottom
                    mathlib.circle(posit, 29, 12); // F -> B corners top
                    mathlib.circle(posit, 31, 10); // F -> B corners bottom
                    mathlib.circle(posit, 30, 11); // F -> B edge
                    mathlib.circle(posit, 20, 25); // R corners #1
                    mathlib.circle(posit, 22, 23); // R corners #2
                    mathlib.circle(posit, 21, 24); // R edges
                }
                if (move == 'F2') {
                    mathlib.circle(posit, 17, 2); // U -> D corners left
                    mathlib.circle(posit, 19, 0); // U -> D corners right
                    mathlib.circle(posit, 7, 22); // L -> R corners top
                    mathlib.circle(posit, 9, 20); // L -> R corners bottom
                    mathlib.circle(posit, 8, 21); // L -> R edges
                    mathlib.circle(posit, 27, 30); // F edges
                    mathlib.circle(posit, 26, 31); // F corners #1
                    mathlib.circle(posit, 28, 29); // F corners #2
                }
            }

            function face(f) {

                size = 2;
                longSize = 3;

                if (!colors) {
                    setColors();
                    colors = cube_colors;
                }

                var leftOffset = 1;
                var topOffset = 2;

                var offx = 10 / 8,
                    offy = 10 / 8;
                if (f == 0) { //D
                    offx *= size;
                    offx += leftOffset;
                    offy *= size * 2.4
                    offy += topOffset;
                } else if (f == 1) { //L
                    offx *= 0;
                    offx += leftOffset;
                    offy *= size;
                    offy += topOffset;
                } else if (f == 2) { //B
                    offx *= size * 3;
                    offx += leftOffset;
                    offy *= size;
                    offy += topOffset;
                } else if (f == 3) { //U
                    offx *= size;
                    offx += leftOffset;
                    offy *= 0;
                    offy += topOffset;
                } else if (f == 4) { //R
                    offx *= size * 2;
                    offx += leftOffset;
                    offy *= size;
                    offy += topOffset;
                } else if (f == 5) { //F
                    offx *= size;
                    offx += leftOffset;
                    offy *= size;
                    offy += topOffset;
                }

                if (f == 3 || f == 0) {

                    var cnt = 0;
                    if (f == 3) {
                        cnt = 16;
                    } else {
                        cnt = 0;
                    }

                    for (var i = 0; i < size; i++) {
                        for (var j = 0; j < size; j++) {
                            drawPolygon(ctx, colors[posit[cnt]], [
                                [i, i, i + 1, i + 1],
                                [j, j + 1, j + 1, j]
                            ], [width, offx, offy]);
                            cnt += 1;
                        }
                    }
                } else {

                    var cnt = 0;
                    if (f == 1) {
                        cnt = 4;
                    } else if (f == 5) {
                        cnt = 26;
                    } else if (f == 4) {
                        cnt = 20;
                    } else {
                        cnt = 10;
                    }

                    for (var i = 0; i < size; i++) {
                        for (var j = 0; j < longSize; j++) {
                            drawPolygon(ctx, colors[posit[cnt]], [
                                [i, i, i + 1, i + 1],
                                [j, j + 1, j + 1, j]
                            ], [width, offx, offy]);
                            cnt += 1;
                        }
                    }
                }
            }

            return function(moveseq) {
                var cnt = 0;
                for (var i = 0; i < 6; i++) {
                    var faceSize = (i == 3 || i == 0) ? 4 : 6;
                    for (var f = 0; f < faceSize; f++) {
                        posit[cnt++] = i;
                    }
                }

                var scramble = moveseq.split(' ');
                for (var i = 0; i < scramble.length; i++) {
                    doMove(scramble[i]);
                }

                var imgSize = scalingFactor / 40;
                canvas.width(35 * imgSize + 'em');
                canvas.height((25 * imgSize)*1.25 + 'em');

                canvas.attr('width', 35 * 3 / 9 * width + 1);
                canvas.attr('height', 25 * 4 / 9 * width + 1);

                for (var i = 0; i < 6; i++) {
                    face(i);
                }
            }
        })();

        var nnnImage = (function() {
            var width = 30;

            var posit = [];

            var colors = null;

            function face(f, size, isVoidCube, is332) {

                setColors();
                colors = cube_colors;

                var offx = 9.8 / 9,
                    offy = 9.8 / 9;
                if (f == 0) { //D
                    offx *= size;
                    offy *= size * 2;
                } else if (f == 1) { //L
                    offx *= 0;
                    offy *= size;
                } else if (f == 2) { //B
                    offx *= size * 3;
                    offy *= size;
                } else if (f == 3) { //U
                    offx *= size;
                    offy *= 0;
                } else if (f == 4) { //R
                    offx *= size * 2;
                    offy *= size;
                } else if (f == 5) { //F
                    offx *= size;
                    offy *= size;
                }

                offy += 0.1;
                offx += 0.1;

                var adjustedOffy = 0;
                var initialOffy = offy;

                do_override = false;
                overrides = null;
                if (size == 3) {
                    do_override = true;
                    overrides = [0, 0, 0, 0];
                }

                center_override = [15, 15, 15, 15];
                edges_override = [0, 0, 0, 0];
                corners_override = [0, 0, 0, 0];

                for (var i = 0; i < size; i++) {
                    var x = (f == 1 || f == 2) ? size - 1 - i : i;
                    for (var j = 0; j < size; j++) {
                        var y = (f == 0) ? size - 1 - j : j;

                        var c = "" + x + "," + y;

                        overrides = [0, 0, 0, 0];
                        if (x == 1 && y == 1) {
                            overrides = center_override;
                        }

                        // set color as normal, unless the void cube flag is set and the piece we're coloring
                        // is not an edge or corner
                        var color = colors[posit[(f * size + y) * size + x]];
                        if (isVoidCube && (![0,size-1].includes(i)) && (![0,size-1].includes(j))) {
                            color = TRANSPARENT;
                        }

                        if (is332 && (j == 1) && [1,5,4,2].includes(f)) { continue; }
                        if (is332) {
                            if (f == 0) {
                                adjustedOffy = initialOffy - 0.5;
                            } else if (f == 3) {
                                adjustedOffy = initialOffy + 0.5;
                            } else {
                                if (j == 0) {
                                    adjustedOffy = initialOffy + 0.5;
                                } else {
                                    adjustedOffy = initialOffy - 0.5;
                                }
                            }
                            offy = adjustedOffy;
                        }

                        drawPolygon(ctx, color, [
                            [i, i, i + 1, i + 1],
                            [j, j + 1, j + 1, j]
                        ], [width, offx, offy], c, do_override, overrides);
                    }
                }
            }

            /**
             *  f: face, [ D L B U R F ]
             *  d: which slice, in [0, size-1)
             *  q: [  2 ']
             */
            function doslice(f, d, q, size) {
                var f1, f2, f3, f4;
                var s2 = size * size;
                var c, i, j, k;
                if (f > 5) f -= 6;
                for (k = 0; k < q; k++) {
                    for (i = 0; i < size; i++) {
                        if (f == 0) {
                            f1 = 6 * s2 - size * d - size + i;
                            f2 = 2 * s2 - size * d - 1 - i;
                            f3 = 3 * s2 - size * d - 1 - i;
                            f4 = 5 * s2 - size * d - size + i;
                        } else if (f == 1) {
                            f1 = 3 * s2 + d + size * i;
                            f2 = 3 * s2 + d - size * (i + 1);
                            f3 = s2 + d - size * (i + 1);
                            f4 = 5 * s2 + d + size * i;
                        } else if (f == 2) {
                            f1 = 3 * s2 + d * size + i;
                            f2 = 4 * s2 + size - 1 - d + size * i;
                            f3 = d * size + size - 1 - i;
                            f4 = 2 * s2 - 1 - d - size * i;
                        } else if (f == 3) {
                            f1 = 4 * s2 + d * size + size - 1 - i;
                            f2 = 2 * s2 + d * size + i;
                            f3 = s2 + d * size + i;
                            f4 = 5 * s2 + d * size + size - 1 - i;
                        } else if (f == 4) {
                            f1 = 6 * s2 - 1 - d - size * i;
                            f2 = size - 1 - d + size * i;
                            f3 = 2 * s2 + size - 1 - d + size * i;
                            f4 = 4 * s2 - 1 - d - size * i;
                        } else if (f == 5) {
                            f1 = 4 * s2 - size - d * size + i;
                            f2 = 2 * s2 - size + d - size * i;
                            f3 = s2 - 1 - d * size - i;
                            f4 = 4 * s2 + d + size * i;
                        }
                        c = posit[f1];
                        posit[f1] = posit[f2];
                        posit[f2] = posit[f3];
                        posit[f3] = posit[f4];
                        posit[f4] = c;
                    }
                    if (d == 0) {
                        for (i = 0; i + i < size; i++) {
                            for (j = 0; j + j < size - 1; j++) {
                                f1 = f * s2 + i + j * size;
                                f3 = f * s2 + (size - 1 - i) + (size - 1 - j) * size;
                                if (f < 3) {
                                    f2 = f * s2 + (size - 1 - j) + i * size;
                                    f4 = f * s2 + j + (size - 1 - i) * size;
                                } else {
                                    f4 = f * s2 + (size - 1 - j) + i * size;
                                    f2 = f * s2 + j + (size - 1 - i) * size;
                                }
                                c = posit[f1];
                                posit[f1] = posit[f2];
                                posit[f2] = posit[f3];
                                posit[f3] = posit[f4];
                                posit[f4] = c;
                            }
                        }
                    }
                }
            }

            return function(size, moveseq, isVoidCube, is332, returnCubeState) {

                isVoidCube = isVoidCube || false; // default value of false
                is332 = is332 || false; // default value of false
                returnCubeState = returnCubeState || false; // default value of false

                var cnt = 0;
                for (var i = 0; i < 6; i++) {
                    for (var f = 0; f < size * size; f++) {
                        posit[cnt++] = i;
                    }
                }
                var moves = parseScramble(moveseq, "DLBURF");
                for (var s = 0; s < moves.length; s++) {
                    for (var d = 0; d < moves[s][1]; d++) {
                        doslice(moves[s][0], d, moves[s][2], size)
                    }
                    if (moves[s][1] == -1) {
                        for (var d = 0; d < size - 1; d++) {
                            doslice(moves[s][0], d, -moves[s][2], size);
                        }
                        doslice((moves[s][0] + 3) % 6, 0, moves[s][2] + 4, size);
                    }
                }

                if (returnCubeState) { return posit; }

                var imgSize = scalingFactor / 50;
                canvas.width(39 * imgSize + 'em');
                canvas.height(29 * imgSize + 'em');

                canvas.attr('width', 39 * size / 9 * width + 1);
                canvas.attr('height', 29 * size / 9 * width + 1);

                for (var i = 0; i < 6; i++) {
                    face(i, size, isVoidCube, is332);
                }
            }
        })();

        var mirrorBlocksImage = (function() {
            var width = 30;

            /**
             * Mirror blocks geometry notes
             *
             * E/M/S slices are all 19 mm wide.
             * This is the reference width, so the multiplier is 1.
             * Using https://rubiks.fandom.com/wiki/Mirror_Cube as a ref
             * for width values and which face thickness is which.
             *
             * U is  9 mm -->  9/19 = 0.474
             * D is 29 mm --> 29/19 = 1.526
             * L is 13 mm --> 13/19 = 0.684
             * R is 25 mm --> 25/19 = 1.316
             * F is 17 mm --> 17/19 = 0.895
             * B is 21 mm --> 21/19 = 1.105
             *
             * Each edge sticker is a rectangle, 19 x N mm.
             * Each corner sticker is a rectangle, N x M mm.
             *
             * The map below is to hold each sticker's dimensions
             * so we can render the correct size after scrambling.
             * Reference image for each sticker number's starting position:
             * https://i.imgur.com/uNliZny.png
             *
             * Reference image for i,j coords on each face:
             * https://i.imgur.com/6MgE7rv.png
             */

            var posit = [];

            var uw = 9/19;
            var dw = 29/19;
            var lw = 13/19;
            var rw = 25/19;
            var fw = 17/19;
            var bw = 21/19;

            var stickerWidthMap = {
                // D-adjacent edge stickers
                52: dw, 43: dw, 25: dw, 16: dw,
                // U-adjacent edge stickers
                46: uw, 37: uw, 19: uw, 10: uw,
                // L-adjacent edge stickers
                48: lw, 30: lw, 3: lw, 21: lw,
                // R-adjacent edge stickers
                50: rw, 32: rw, 5: rw, 23: rw,
                // F-adjacent edge stickers
                34: fw, 12: fw, 7: fw, 39: fw,
                // B-adjacent edge stickers
                14: bw, 28: bw, 41: bw, 1: bw,

                // For corners, there isn't a reference 19mm edge
                // so later we need to know if it's in its "native orientation"
                // (its home position on each face, or the opposite corner)
                // or not. Just store (height, width) in that order, and whether it's
                // in the naturally in the top-right or bottom-left spot.

                // F
                51: [[dw, lw], true],
                53: [[dw, rw], false],
                45: [[uw, lw], false],
                47: [[uw, rw], true],

                // D
                0: [[bw, lw], true],
                2: [[bw, rw], false],
                6: [[fw, lw], false],
                8: [[fw, rw], true],

                // R
                42: [[dw, fw], true],
                44: [[dw, bw], false],
                36: [[uw, fw], false],
                38: [[uw, bw], true],

                // B
                26: [[dw, rw], true],
                24: [[dw, lw], false],
                20: [[uw, rw], false],
                18: [[uw, lw], true],

                // L
                17: [[dw, bw], true],
                15: [[dw, fw], false],
                11: [[uw, bw], false],
                 9: [[uw, fw], true],

                 // U
                 33: [[fw, lw], true],
                 35: [[fw, rw], false],
                 27: [[bw, lw], false],
                 29: [[bw, rw], true]
            }

            var centers = [4, 13, 49, 40, 22, 31];
            var edges = [1, 3, 5, 7, 10, 12, 14, 16, 19, 21, 23, 25, 28, 30, 32, 34, 37, 39, 41, 43, 46, 48, 50, 52];

            function face(f, size) {

                var adj_width = width * 0.7;

                var offx = 13 / 9;
                var offy = 13 / 9;

                if (f == 0) { //D
                    offx *= size;
                    offy *= size * 2;
                } else if (f == 1) { //L
                    offx *= 0;
                    offy *= size;
                } else if (f == 2) { //B
                    offx *= size * 3;
                    offy *= size;
                } else if (f == 3) { //U
                    offx *= size;
                    offy *= 0;
                } else if (f == 4) { //R
                    offx *= size * 2;
                    offy *= size;
                } else if (f == 5) { //F
                    offx *= size;
                    offy *= size;
                }

                offy += 0.5;
                offx += 0.5;

                var polysToDraw = [];

                for (var i = 0; i < size; i++) {
                    var x = (f == 1 || f == 2) ? size - 1 - i : i;
                    for (var j = 0; j < size; j++) {
                        var y = (f == 0) ? size - 1 - j : j;

                        var stickerIndex = (f * size + y) * size + x;
                        var stickerNum = posit[stickerIndex];
                        var x_coords;
                        var y_coords;

                        if (centers.includes(stickerNum))
                        {
                            x_coords = [i, i, i + 1, i + 1];
                            y_coords = [j, j + 1, j + 1, j];
                        } 
                        else if (edges.includes(stickerNum))
                        {
                            var alt_w = stickerWidthMap[stickerNum];

                            // it's an upper or lower sticker
                            if (i == 1) {
                                x_coords = [i, i, i + 1, i + 1];
                                if (j == 0) {  // upper
                                    y_coords = [j + 1 - alt_w, j + 1, j + 1, j + 1 - alt_w];
                                } else {       // lower
                                   y_coords = [j, j + alt_w, j + alt_w, j];
                                }
                            }

                            // else it's a left or right sticker
                            else {
                                y_coords = [j, j + 1, j + 1, j];
                                if (i == 0) {  // left
                                    x_coords = [i + 1 - alt_w, i + 1 - alt_w, i + 1, i + 1];
                                } else {      // right
                                    x_coords = [i, i, i + alt_w, i + alt_w];
                                }
                            }
                        }
                        else
                        {
                            // [[h, w], belongsInPrimaryPos]
                            var stickerInfo = stickerWidthMap[stickerNum];
                            var belongsInPrimaryPos = stickerInfo[1];
                            var alt_w = stickerInfo[0][1];
                            var alt_h = stickerInfo[0][0];

                            // i, j
                            if (i == 0 && j == 0) // upper-left
                            {
                                // * not primary pos
                                if (belongsInPrimaryPos) {
                                    var tmp = alt_h;
                                    alt_h = alt_w;
                                    alt_w = tmp;
                                }

                                x_coords = [i + 1 - alt_w, i + 1 - alt_w, i + 1, i + 1];
                                y_coords = [j + 1 - alt_h, j + 1, j + 1, j + 1 - alt_h];
                            }
                            else if (i == 2 && j == 0) // upper-right
                            {
                                // * primary pos
                                if (!belongsInPrimaryPos) {
                                    var tmp = alt_h;
                                    alt_h = alt_w;
                                    alt_w = tmp;
                                }

                                x_coords = [i, i, i + alt_w, i + alt_w];
                                y_coords = [j + 1 - alt_h, j + 1, j + 1, j + 1 - alt_h];
                            }
                            else if (i == 0 && j == 2) // bottom-left
                            {
                                // * primary pos
                                if (!belongsInPrimaryPos) {
                                    var tmp = alt_h;
                                    alt_h = alt_w;
                                    alt_w = tmp;
                                }

                                x_coords = [i + 1 - alt_w, i + 1 - alt_w, i + 1, i + 1];
                                y_coords = [j, j + alt_h, j + alt_h, j];
                            }
                            else  // bottom-right
                            {
                                // * not primary pos
                                if (belongsInPrimaryPos) {
                                    var tmp = alt_h;
                                    alt_h = alt_w;
                                    alt_w = tmp;
                                }

                                x_coords = [i, i, i + alt_w, i + alt_w];
                                y_coords = [j, j + alt_h, j + alt_h, j];
                            }
                        }
                        polysToDraw.push([x_coords, y_coords]);
                    }
                }

                var all_x = [];
                var all_y = [];
                for (var n = 0; n < polysToDraw.length; n++) {
                    var coords = polysToDraw[n];
                    var sticker_x = coords[0];
                    var sticker_y = coords[1];
                    for (var ni = 0; ni < 4; ni++) {
                        all_x.push(sticker_x[ni]);
                        all_y.push(sticker_y[ni]);
                    }
                }

                // Do some centering and alignment adjustment of the faces
                var min_x = Math.min(...all_x);
                var min_y = Math.min(...all_y);
                var max_x = Math.max(...all_x);
                var max_y = Math.max(...all_y);

                var total_width = max_x - min_x;
                var total_height = max_y - min_y;
                for (var n = 0; n < polysToDraw.length; n++) {
                    var coords = polysToDraw[n];
                    var sticker_x = coords[0];
                    var sticker_y = coords[1];
                    for (var ni = 0; ni < 4; ni++) {
                        // Only center vertically and horizontally on the appropriate faces, to make sure the E and M slices
                        // stay visually aligned.
                        if (![0, 3, 5].includes(f)) {
                            sticker_x[ni] = sticker_x[ni] - min_x + ((3 - total_width) / 2);
                        }
                        if (![1, 5, 4, 2].includes(f)) {
                            sticker_y[ni] = sticker_y[ni] - min_y + ((3 - total_height) / 2);
                        }
                    }
                }

                for (var n = 0; n < polysToDraw.length; n++) {
                    var coords = polysToDraw[n];
                    drawPolygon(ctx, "#C0C0C0", [
                        coords[0],
                        coords[1],
                    ], [adj_width, offx, offy]);
                }
            }

            /**
             *  f: face, [ D L B U R F ]
             *  d: which slice, in [0, size-1)
             *  q: [  2 ']
             */
            function doslice(f, d, q, size) {

                var f1, f2, f3, f4;
                var s2 = size * size;
                var c, i, j, k;
                if (f > 5) f -= 6;
                for (k = 0; k < q; k++) {
                    for (i = 0; i < size; i++) {
                        if (f == 0) {
                            f1 = 6 * s2 - size * d - size + i;
                            f2 = 2 * s2 - size * d - 1 - i;
                            f3 = 3 * s2 - size * d - 1 - i;
                            f4 = 5 * s2 - size * d - size + i;
                        } else if (f == 1) {
                            f1 = 3 * s2 + d + size * i;
                            f2 = 3 * s2 + d - size * (i + 1);
                            f3 = s2 + d - size * (i + 1);
                            f4 = 5 * s2 + d + size * i;
                        } else if (f == 2) {
                            f1 = 3 * s2 + d * size + i;
                            f2 = 4 * s2 + size - 1 - d + size * i;
                            f3 = d * size + size - 1 - i;
                            f4 = 2 * s2 - 1 - d - size * i;
                        } else if (f == 3) {
                            f1 = 4 * s2 + d * size + size - 1 - i;
                            f2 = 2 * s2 + d * size + i;
                            f3 = s2 + d * size + i;
                            f4 = 5 * s2 + d * size + size - 1 - i;
                        } else if (f == 4) {
                            f1 = 6 * s2 - 1 - d - size * i;
                            f2 = size - 1 - d + size * i;
                            f3 = 2 * s2 + size - 1 - d + size * i;
                            f4 = 4 * s2 - 1 - d - size * i;
                        } else if (f == 5) {
                            f1 = 4 * s2 - size - d * size + i;
                            f2 = 2 * s2 - size + d - size * i;
                            f3 = s2 - 1 - d * size - i;
                            f4 = 4 * s2 + d + size * i;
                        }
                        c = posit[f1];
                        posit[f1] = posit[f2];
                        posit[f2] = posit[f3];
                        posit[f3] = posit[f4];
                        posit[f4] = c;
                    }
                    if (d == 0) {
                        for (i = 0; i + i < size; i++) {
                            for (j = 0; j + j < size - 1; j++) {
                                f1 = f * s2 + i + j * size;
                                f3 = f * s2 + (size - 1 - i) + (size - 1 - j) * size;
                                if (f < 3) {
                                    f2 = f * s2 + (size - 1 - j) + i * size;
                                    f4 = f * s2 + j + (size - 1 - i) * size;
                                } else {
                                    f4 = f * s2 + (size - 1 - j) + i * size;
                                    f2 = f * s2 + j + (size - 1 - i) * size;
                                }
                                c = posit[f1];
                                posit[f1] = posit[f2];
                                posit[f2] = posit[f3];
                                posit[f3] = posit[f4];
                                posit[f4] = c;
                            }
                        }
                    }
                }
            }

            return function(size, moveseq) {
                var cnt = 0;
                for (var i = 0; i < 6; i++) {
                    for (var f = 0; f < size * size; f++) {
                        posit[cnt] = cnt;
                        cnt += 1;
                    }
                }
                var moves = parseScramble(moveseq, "DLBURF");
                for (var s = 0; s < moves.length; s++) {
                    for (var d = 0; d < moves[s][1]; d++) {
                        doslice(moves[s][0], d, moves[s][2], size)
                    }
                    if (moves[s][1] == -1) {
                        for (var d = 0; d < size - 1; d++) {
                            doslice(moves[s][0], d, -moves[s][2], size);
                        }
                        doslice((moves[s][0] + 3) % 6, 0, moves[s][2] + 4, size);
                    }
                }

                var imgSize = scalingFactor / 50;
                canvas.width(39 * imgSize + 'em');
                canvas.height(29 * imgSize + 'em');

                canvas.attr('width', 39 * size / 9 * width + 1);
                canvas.attr('height', 29 * size / 9 * width + 1);

                for (var i = 0; i < 6; i++) {
                    face(i, size);
                }
            }
        })();

        var types_nnn = ['', '', '2x2', '3x3', '4x4', '5x5', '6x6', '7x7', '8x8', '9x9', '10x10'];

        function setBorderRadius(type, canvasSize) {
            cornerRadiusOptions = cornerRadiusMap[type] || defaultCornerRadiusOptions;
            eventCornerRadius = cornerRadiusOptions[canvasSize];
        }

        function genImage(scramble, canvasSize) {

            var type = scramble[0];
            var scrambleText = scramble[1];

            // If the event is complete, don't event bother trying to parse
            // a real scramble. Just use an empty string in place of scramble.
            if (window.app.isComplete) {
                scrambleText = '';
            }

            setBorderRadius(type, canvasSize);

            var size;
            for (size = 0; size <= 10; size++) {
                if (type == types_nnn[size]) {
                    nnnImage(size, scrambleText);
                    return true;
                }
            }
            if (type == "3x3OH" || type == "2GEN" || type == "LSE" || type == "F2L" || type == "3x3 With Feet" || type == "FMC" || type == "COLL") {
                nnnImage(3, scrambleText);
                return true;
            }
            if (type == "Void Cube") {
                nnnImage(3, scrambleText, true);
                return true;
            }
            if (type == "3x3x2") {
                nnnImage(3, scrambleText, false, true);
                return true;
            }
            if (type == "Mirror Blocks" || type == "3x3 Mirror Blocks/Bump") {
                mirrorBlocksImage(3, scrambleText);
                return true;
            }
            if (type == "Redi Cube") {
                rediImage(scrambleText);
                return true;
            }
            if (type == "Dino Cube") {
                dinoImage(scrambleText);
                return true;
            }
            if (type == "3x3x4") {
                image334(scrambleText);
                return true;
            }
            if (type == "2x2x3") {
                image223(scrambleText);
                return true;
            }
            if (type == "4x4 OH") {
                nnnImage(4, scrambleText);
                return true;
            }
            if (type == "Pyraminx") {
                pyraImage(scrambleText);
                return true;
            }
            if (type == "Skewb") {
                skewbImage(scrambleText);
                return true;
            }
            if (type == "Rex Cube") {
                rexImage(scrambleText);
                return true;
            }
            if (type == "Square-1") {
                sq1Image(scrambleText);
                return true;
            }
            if (type == "Clock") {
                clkImage(scrambleText);
                return true;
            }
            if (type == "Megaminx") {
                mgmImage(scrambleText);
                return true;
            }
            if (type == "Kilominx") {
                kilominxImage(scrambleText);
                return true;
            }
            if (type == "15 Puzzle") {
                fifteenImage(scrambleText);
                return true;
            }
            if (type == "FTO") {
                ftoImage(scrambleText);
                return true;
            }
            return false;
        }

        function getCubeState(scramble) {
            return nnnImage(3, scramble, false, false, true);
        }

        function getCanvasWidth() {
            return parseInt($(canvas[0]).css('width').replace('px',''));
        }

        function getCanvasHeight() {
            return parseInt($(canvas[0]).css('height').replace('px',''));
        }

        function setScalingFactorDirectly(size) {
            scalingFactor = size;
        }

        function clearCanvas() {
            ctx.clearRect(0, 0, canvas[0].width, canvas[0].height);
        }

        function findCanvas(canvasId) {
            canvas = $(canvasId);
            if (canvas.length == 0) {
                return false;
            }
            if (!canvas[0].getContext) {
                return false;
            }
            ctx = canvas[0].getContext('2d');
            return true;
        }

        return {
            draw: genImage,
            drawPolygon: drawPolygon,
            findCanvas: findCanvas,
            clearCanvas: clearCanvas,
            setScalingFactorDirectly: setScalingFactorDirectly,
            getCanvasWidth: getCanvasWidth,
            getCanvasHeight: getCanvasHeight,
            getCubeState: getCubeState
        }
    })();

    /**
     * Utility class for generating puzzle scrambles.
     */
    function ScrambleImageGenerator() {
        this.largeCanvasId = '#big_scramble_image';
        this.normalCanvasId = '#normal_scramble_image';
        this.largeScalingFactor = 10;
        this.haveEstablishedLargeScalingFactor = false;
        this.desktopScalingFactor = 10;
        this.haveEstablishedDesktopScalingFactor = false;

        setColors();

        this.prepareNewImage();

        var resetImageScalingAndRenderAgain = function() {
            this.largeScalingFactor = 10;
            this.haveEstablishedLargeScalingFactor = false;
            this.desktopScalingFactor = 10;
            this.haveEstablishedDesktopScalingFactor = false;
            this.showNormalImage();
        };
        $(window).resize(resetImageScalingAndRenderAgain.bind(this));
    }

    ScrambleImageGenerator.prototype.replaceScramble = function(newScramble) {

        this.savedScramble = newScramble

        // If the event is COLL, extract the actual scramble part, which should be the final thing after a line break
        if (this.savedEventName == 'COLL') {
            this.savedScramble = this.savedScramble.split('<br/>').pop();
        }

        // Attempt to draw normal image. If we're on mobile, the normal canvas won't exist
        // and it'll just bail early.
        this.showNormalImage();
    };

    ScrambleImageGenerator.prototype.prepareNewImage = function() {

        // Store these for later in case in case the user takes action to show a bigger scramble image
        this.savedScramble = app.scramble;
        this.savedEventName = app.eventName;

        // If the event is COLL, extract the actual scramble part, which should be the final thing after a line break
        if (this.savedEventName == 'COLL') {
            this.savedScramble = this.savedScramble.split('<br/>').pop();
        }

        // Attempt to draw normal image. If we're on mobile, the normal canvas won't exist
        // and it'll just bail early.
        this.showNormalImage();
    };

    ScrambleImageGenerator.prototype.getCubeState = function(scramble) {
        return image.getCubeState(scramble).join('');
    }

    ScrambleImageGenerator.prototype.getAllSolvedCubeStates = function(scramble) {
        var states = [];
        
        // top, front
        states.push(image.getCubeState("").join(''));      // white, green
        states.push(image.getCubeState("y").join(''));     // white, red 
        states.push(image.getCubeState("y2").join(''));    // white, blue
        states.push(image.getCubeState("y'").join(''));    // white, orange
        states.push(image.getCubeState("x").join(''));     // green, yellow
        states.push(image.getCubeState("x y").join(''));   // green, red 
        states.push(image.getCubeState("x y2").join(''));  // green, white
        states.push(image.getCubeState("x y'").join(''));  // green, orange
        states.push(image.getCubeState("x2").join(''));    // yellow, blue
        states.push(image.getCubeState("x2 y").join(''));  // yellow, red 
        states.push(image.getCubeState("x2 y2").join('')); // yellow, green
        states.push(image.getCubeState("x2 y'").join('')); // yellow, orange
        states.push(image.getCubeState("x'").join(''));    // blue, white
        states.push(image.getCubeState("x' y").join(''));  // blue, red 
        states.push(image.getCubeState("x' y2").join('')); // blue, yellow
        states.push(image.getCubeState("x' y'").join('')); // blue, orange
        states.push(image.getCubeState("z").join(''));     // orange, green
        states.push(image.getCubeState("z y").join(''));   // orange, white
        states.push(image.getCubeState("z y2").join(''));  // orange, blue
        states.push(image.getCubeState("z y'").join(''));  // orange, yellow
        states.push(image.getCubeState("z'").join(''));    // red, green
        states.push(image.getCubeState("z' y").join(''));  // red, yellow
        states.push(image.getCubeState("z' y2").join('')); // red, blue
        states.push(image.getCubeState("z' y'").join('')); // red, white

        return states;
    }

    ScrambleImageGenerator.prototype.showNormalImage = function() {
        // If the canvas doesn't exist, we shouldn't be trying to show the image, just bail
        if (!image.findCanvas(this.normalCanvasId)) { return; }

        // If we have already established the right scaling factor for this puzzle
        // on this window size, just go ahead and draw the image that was prepped
        if (this.haveEstablishedDesktopScalingFactor) {
            image.setScalingFactorDirectly(this.desktopScalingFactor);
            return image.draw([this.savedEventName, this.savedScramble], CANVAS_SMALL_RADIUS_IDX);
        }

        // Find the correct scaling factor and remember that we've done so
        var targetWidth = $('.scramble_preview').width();
        this.desktopScalingFactor = this.determineScalingFactorAndDraw(targetWidth);
        this.haveEstablishedDesktopScalingFactor = true;

        // Finally draw the preview at the correct scaling factor
        image.setScalingFactorDirectly(this.desktopScalingFactor);
        return image.draw([this.savedEventName, this.savedScramble], CANVAS_SMALL_RADIUS_IDX);
    };

    ScrambleImageGenerator.prototype.showLargeImage = function() {
        // If the canvas doesn't exist, we shouldn't be trying to show the image, just bail
        if (!image.findCanvas(this.largeCanvasId)) { return; }

        // If we have already established the right scaling factor for this puzzle
        // on this device, just go ahead and draw the image that was prepped
        if (this.haveEstablishedLargeScalingFactor) {
            image.setScalingFactorDirectly(this.largeScalingFactor);
            return image.draw([this.savedEventName, this.savedScramble], CANVAS_LARGE_RADIUS_IDX);
        }

        // Target width & height is 20 less than device/browser width & height, so there's a ~10px buffer on either side
        // Find the correct scaling factor and remember that we've done so
        var targetWidth = $(window).width() - 20;
        this.largeScalingFactor = this.determineScalingFactorAndDraw(targetWidth);
        this.haveEstablishedLargeScalingFactor = true;

        // Finally draw the preview at the correct scaling factor
        image.setScalingFactorDirectly(this.largeScalingFactor);
        return image.draw([this.savedEventName, this.savedScramble], CANVAS_LARGE_RADIUS_IDX);
    };

    ScrambleImageGenerator.prototype.determineScalingFactorAndDraw = function(targetWidth) {
        // Start at 10, that's pretty small
        var testScalingFactor = 10;
        while (true) {

            image.setScalingFactorDirectly(testScalingFactor);
            image.draw([this.savedEventName, this.savedScramble], CANVAS_SMALL_RADIUS_IDX);

            if (testScalingFactor >= 50) {
                testScalingFactor = 50;
                break;
            } else if (Math.abs(image.getCanvasWidth() - targetWidth)/(targetWidth) < 0.10) {
                if (window.app.isMobile) {
                    testScalingFactor -= 2;
                }
                if (image.getCanvasWidth() >= targetWidth) {
                    testScalingFactor -= 1;
                }
                break;
            } else {
                // Not big enough yet, pump it up
                testScalingFactor += 1;
            }
        }
        return testScalingFactor;
    };

    ScrambleImageGenerator.prototype._clearImage = function() {
        if (image.findCanvas('#normal_scramble_image')) {
            image.clearCanvas();
        }
        if (image.findCanvas('#big_scramble_image')) {
            image.clearCanvas();
        }
    };

    ScrambleImageGenerator.prototype.injectCubeColors = function(newColors) {
        cube_colors = newColors;
    };

    ScrambleImageGenerator.prototype.injectMegaColors = function(newColors) {
        mega_colors = newColors;
    };

    ScrambleImageGenerator.prototype.injectPyraColors = function(newColors) {
        pyra_colors = newColors;
    };

    ScrambleImageGenerator.prototype.injectFtoColors = function(newColors) {
        fto_colors = newColors;
    };

    ScrambleImageGenerator.prototype.injectSq1Colors = function(newColors) {
        sq1_colors = newColors;
    };

    ScrambleImageGenerator.prototype.injectRexColors = function(newColors) {
        rex_colors = newColors;
    };


    ScrambleImageGenerator.prototype.resetDefaultColors = function() {
        cube_colors = default_cube_colors;
        mega_colors = default_mega_colors;
        pyra_colors = default_pyra_colors;
        fto_colors = default_fto_colors;
        sq1_colors = default_sq1_colors;
        rex_colors = default_rex_colors;
    };

    // Make ScrambleImageGenerator visible at app scope
    window.app.ScrambleImageGenerator = ScrambleImageGenerator;
})();