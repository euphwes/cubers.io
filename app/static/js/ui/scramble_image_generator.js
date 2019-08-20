(function() {
    var app = window.app;

    var cube_colors = [];
    var skewb_colors = [];
    var sq1_colors = {};

    var pyra_colors = [];

    var mega_colors = [];

    var TRANSPARENT = "rgba(255, 255, 255, 0)";

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
            sq1_colors = {
                'U': window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_CUBE_COLOR_U),
                'R': window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_CUBE_COLOR_R),
                'F': window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_CUBE_COLOR_F),
                'D': window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_CUBE_COLOR_D),
                'L': window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_CUBE_COLOR_L),
                'B': window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_CUBE_COLOR_B)
            };
        } else {
            // Order is    D,      L,      B,      U,      R,      F
            cube_colors = ['#ff0', '#fa0', '#00f', '#fff', '#f00', '#0d0'];
            // Order is    U,      B,      R,      D,      F       L
            skewb_colors = ['#fff', '#00f', '#f00', '#ff0', '#0f0', '#f80'];
            sq1_colors = {
                'U': '#ff0',
                'R': '#f80',
                'F': '#0f0',
                'D': '#fff',
                'L': '#f00',
                'B': '#00f'
            };
        }

        if (window.app.userSettingsManager.get_setting(app.Settings.USE_CUSTOM_PYRAMINX_COLORS)) {
            pyra_colors = [
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_PYRAMINX_COLOR_F),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_PYRAMINX_COLOR_L),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_PYRAMINX_COLOR_R),
                window.app.userSettingsManager.get_setting(app.Settings.CUSTOM_PYRAMINX_COLOR_D)
            ];
        } else {
            pyra_colors = ['#0f0', '#f00', '#00f', '#ff0'];
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
        } else {
            mega_colors = ['#fff', '#d00', '#060', '#81f', '#fc0', '#00b', '#ffb', '#8df', '#f83', '#7e0', '#f9f', '#999'];
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

        // trans: [size, offx, offy] == [size, 0, offx * size, 0, size, offy * size] or [a11 a12 a13 a21 a22 a23]
        function drawPolygon(ctx, color, arr, trans, text, is334) {
            if (!ctx) {
                return;
            }
            trans = trans || [1, 0, 0, 0, 1, 0];
            is334 = is334 || false;

            if (is334) {
                trans[0] = trans[0] * 0.80;
            }

            arr = Transform(arr, trans);
            ctx.beginPath();

            ctx.fillStyle = color;
            if(color == TRANSPARENT) {
                ctx.strokeStyle = TRANSPARENT;
            } else {
                ctx.strokeStyle = "#000";
            }

            ctx.moveTo(arr[0][0], arr[1][0]);
            for (var i = 1; i < arr[0].length; i++) {
                ctx.lineTo(arr[0][i], arr[1][i]);
            }
            ctx.closePath();
            ctx.fill();
            ctx.stroke();

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

                if (!colors) {
                    setColors();
                    colors = mega_colors;
                }

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

                if (!colors) {
                    setColors();
                    colors = sq1_colors;
                }

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

                if (!colors) {
                    setColors();
                    colors = pyra_colors;
                }

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

        var image334 = (function() {
            var width = 30;
            var posit = [];
            var colors = null;

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

                if (f == 3 || f == 0) {
                    for (var i = 0; i < size; i++) {
                        var x = (f == 1 || f == 2) ? size - 1 - i : i;
                        for (var j = 0; j < size; j++) {
                            var y = (f == 0) ? size - 1 - j : j;
                            if ((i == 1) && (j == 1)) { continue; }
    
                            var posit_index = (f * size + y) * size + x;
                            // var color = colors[posit[posit_index]];
                            var color = colors[0];

                            drawPolygon(ctx, color, [
                                [i, i, i + 1, i + 1],
                                [j, j + 1, j + 1, j]
                            ], [width, offx, offy]);
                        }
                    }
                } else {
                    for (var i = 0; i < size; i++) {
                        var x = (f == 1 || f == 2) ? size - 1 - i : i;
                        for (var j = 0; j < longSize; j++) {
                            var y = (f == 0) ? size - 1 - j : j;
                            if ((i == 1) && (j == 1)) { continue; }
    
                            var posit_index = (f * size + y) * size + x;
                            var color = colors[0];
                            // var color = colors[posit[posit_index]];
    
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
                canvas.height((29 * imgSize)*1.33 + 'em');

                canvas.attr('width', 39 * 3 / 9 * width + 1);
                canvas.attr('height', 29 * 4 / 9 * width + 1);

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

                var adjustedOffy = 0;
                var initialOffy = offy;

                for (var i = 0; i < size; i++) {
                    var x = (f == 1 || f == 2) ? size - 1 - i : i;
                    for (var j = 0; j < size; j++) {
                        var y = (f == 0) ? size - 1 - j : j;

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
                        ], [width, offx, offy]);
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

            return function(size, moveseq, isVoidCube, is332) {

                isVoidCube = isVoidCube || false; // default value of false
                is332 = is332 || false; // default value of false

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

        var types_nnn = ['', '', '2x2', '3x3', '4x4', '5x5', '6x6', '7x7', '8x8', '9x9'];

        function genImage(scramble) {

            var type = scramble[0];
            var size;
            for (size = 0; size <= 9; size++) {
                if (type == types_nnn[size]) {
                    nnnImage(size, scramble[1]);
                    return true;
                }
            }
            if (type == "3x3OH" || type == "2GEN" || type == "LSE" || type == "F2L" || type == "3x3 With Feet" || type == "FMC" || type == "COLL") {
                nnnImage(3, scramble[1]);
                return true;
            }
            if (type == "Void Cube") {
                nnnImage(3, scramble[1], true);
                return true;
            }
            if (type == "3x3x2") {
                nnnImage(3, scramble[1], false, true);
                return true;
            }
            if (type == "Redi Cube") {
                rediImage(scramble[1]);
                return true;
            }
            if (type == "Dino Cube") {
                dinoImage(scramble[1]);
                return true;
            }
            if (type == "3x3x4") {
                image334(scramble[1]);
                return true;
            }
            if (type == "4x4 OH") {
                nnnImage(4, scramble[1]);
                return true;
            }
            if (type == "Pyraminx") {
                pyraImage(scramble[1]);
                return true;
            }
            if (type == "Skewb") {
                skewbImage(scramble[1]);
                return true;
            }
            if (type == "Square-1") {
                sq1Image(scramble[1]);
                return true;
            }
            if (type == "Clock") {
                clkImage(scramble[1]);
                return true;
            }
            if (type == "Megaminx") {
                mgmImage(scramble[1]);
                return true;
            }
            return false;
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

    ScrambleImageGenerator.prototype.showNormalImage = function() {
        // If the canvas doesn't exist, we shouldn't be trying to show the image, just bail
        if (!image.findCanvas(this.normalCanvasId)) { return; }

        // If we have already established the right scaling factor for this puzzle
        // on this window size, just go ahead and draw the image that was prepped
        if (this.haveEstablishedDesktopScalingFactor) {
            image.setScalingFactorDirectly(this.desktopScalingFactor);
            return image.draw([this.savedEventName, this.savedScramble]);
        }

        // Find the correct scaling factor and remember that we've done so
        var targetWidth = $('.scramble_preview').width();
        this.desktopScalingFactor = this.determineScalingFactorAndDraw(targetWidth);
        this.haveEstablishedDesktopScalingFactor = true;

        // Finally draw the preview at the correct scaling factor
        image.setScalingFactorDirectly(this.desktopScalingFactor);
        return image.draw([this.savedEventName, this.savedScramble]);
    };

    ScrambleImageGenerator.prototype.showLargeImage = function() {
        // If the canvas doesn't exist, we shouldn't be trying to show the image, just bail
        if (!image.findCanvas(this.largeCanvasId)) { return; }

        // If we have already established the right scaling factor for this puzzle
        // on this device, just go ahead and draw the image that was prepped
        if (this.haveEstablishedLargeScalingFactor) {
            image.setScalingFactorDirectly(this.largeScalingFactor);
            return image.draw([this.savedEventName, this.savedScramble]);
        }

        // Target width & height is 20 less than device/browser width & height, so there's a ~10px buffer on either side
        // Find the correct scaling factor and remember that we've done so
        var targetWidth = $(window).width() - 20;
        this.largeScalingFactor = this.determineScalingFactorAndDraw(targetWidth);
        this.haveEstablishedLargeScalingFactor = true;

        // Finally draw the preview at the correct scaling factor
        image.setScalingFactorDirectly(this.largeScalingFactor);
        return image.draw([this.savedEventName, this.savedScramble]);
    };

    ScrambleImageGenerator.prototype.determineScalingFactorAndDraw = function(targetWidth) {
        // Start at 10, that's pretty small
        var testScalingFactor = 10;
        while (true) {

            image.setScalingFactorDirectly(testScalingFactor);
            image.draw([this.savedEventName, this.savedScramble]);

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

    // Make ScrambleImageGenerator visible at app scope
    window.app.ScrambleImageGenerator = ScrambleImageGenerator;
})();