from src.config.betmode import BetMode
from src.config.distributions import Distribution
from src.config.config import Config
import os


class GameConfig(Config):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

        # ── Identity ──────────────────────────────────────────────────────────
        self.rtp = 0.96
        self.game_id = "LemonLabs_1_96"
        self.provider_name = "Lemon_Labs"
        self.provider_number = 1
        self.working_name = "Castle Fortune"
        self.wincap = 10000.0
        self.win_type = "lines"
        self.construct_paths()

        # ── Grid ──────────────────────────────────────────────────────────────
        self.num_reels = 5
        self.num_rows = [4] * self.num_reels

        # ── Paytable ──────────────────────────────────────────────────────────
        self.paytable = {
            (5, "W"):  25,  (4, "W"):  10,  (3, "W"):  5,
            (5, "H1"): 25,  (4, "H1"): 10,  (3, "H1"): 5,
            (5, "H2"): 10,  (4, "H2"): 4,   (3, "H2"): 2,
            (5, "H3"): 7,   (4, "H3"): 2,   (3, "H3"): 1,
            (5, "H4"): 5,   (4, "H4"): 1.5, (3, "H4"): 0.5,
            (5, "L1"): 3,   (4, "L1"): 0.7, (3, "L1"): 0.3,
            (5, "L2"): 2,   (4, "L2"): 0.5, (3, "L2"): 0.2,
            (5, "L3"): 2,   (4, "L3"): 0.5, (3, "L3"): 0.2,
            (5, "L4"): 1,   (4, "L4"): 0.3, (3, "L4"): 0.1,
            (5, "L5"): 0.5, (4, "L5"): 0.2, (3, "L5"): 0.05,
        }

        # ── Paylines (5x4, 25 lines) ──────────────────────────────────────────
        self.paylines = {
            # Straight horizontals
            1:  [0, 0, 0, 0, 0],
            2:  [1, 1, 1, 1, 1],
            3:  [2, 2, 2, 2, 2],
            4:  [3, 3, 3, 3, 3],
            # V shapes
            5:  [0, 1, 2, 1, 0],
            6:  [1, 2, 3, 2, 1],
            7:  [3, 2, 1, 2, 3],
            8:  [2, 1, 0, 1, 2],
            # Diagonals
            9:  [0, 1, 2, 3, 3],
            10: [0, 0, 1, 2, 3],
            11: [3, 2, 1, 0, 0],
            12: [3, 3, 2, 1, 0],
            # Zigzags
            13: [0, 1, 1, 1, 2],
            14: [2, 1, 1, 1, 0],
            15: [1, 2, 2, 2, 1],
            16: [2, 3, 3, 3, 2],
            17: [1, 0, 0, 0, 1],
            18: [2, 3, 2, 3, 2],
            19: [1, 0, 1, 0, 1],
            # W / M shapes
            20: [0, 2, 0, 2, 0],
            21: [3, 1, 3, 1, 3],
            22: [0, 3, 1, 3, 0],
            23: [3, 0, 2, 0, 3],
            # Mixed
            24: [1, 2, 3, 2, 3],
            25: [2, 1, 0, 1, 0],
        }

        # ── Symbols ───────────────────────────────────────────────────────────
        # W  = Wild — always substitutes at 2x
        #      forms super wild blocks when adjacent Wilds land:
        #        2x2 block → wildQuad  event, +random(10-25) to total multiplier
        #        3x3 block → wildQuad3 event, +random(10-25) to total multiplier
        #        4x4 block → wildQuad4 event, +random(10-25) to total multiplier
        #      single wilds not in a block each add +2 to total multiplier
        # S  = Scatter (triggers freespins)
        self.include_padding = True
        self.special_symbols = {
            "wild":    ["W"],
            "scatter": ["S"],
        }

        # ── Freespin triggers ─────────────────────────────────────────────────
        self.freespin_triggers = {
            self.basegame_type: {3: 10, 4: 15, 5: 20},
            self.freegame_type: {2: 3,  3: 5,  4: 10, 5: 15},
        }

        self.anticipation_triggers = {
            self.basegame_type: 2,
            self.freegame_type: 2,
        }

        # ── Reelstrips ────────────────────────────────────────────────────────
        # Wild blocks land naturally from BR0/FR0.
        # Tune Wild frequency in those CSVs to control block hit rate.
        reel_files = {
            "BR0":  "BR0.csv",
            "FR0":  "FR0.csv",
            "WCAP": "FRWCAP.csv",
        }
        self.reels = {
            key: self.read_reels_csv(os.path.join(self.reels_path, fname))
            for key, fname in reel_files.items()
        }
        self.padding_reels[self.basegame_type] = self.reels["BR0"]
        self.padding_reels[self.freegame_type] = self.reels["FR0"]

        # Padding wilds are always 2x — no random distribution needed
        self.padding_symbol_values = {
            "W": {"multiplier": {2: 1}}
        }

        # ── Simulation conditions ─────────────────────────────────────────────
        # mult_values are always {2: 1} across all conditions.
        # Wilds are locked at 2x substitution value in game_override.py.
        # Block multipliers (10-25) are applied separately in game_executables.py.

        basegame_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
            },
            "mult_values": {
                self.basegame_type: {2: 1},
            },
            "force_wincap":   False,
            "force_freegame": False,
        }

        freegame_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1},
            },
            "scatter_triggers": {3: 50, 4: 20, 5: 5},
            "mult_values": {
                self.basegame_type: {2: 1},
                self.freegame_type: {2: 1},
            },
            "force_wincap":   False,
            "force_freegame": True,
        }

        wincap_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1, "WCAP": 5},
            },
            "scatter_triggers": {4: 1, 5: 2},
            "mult_values": {
                self.basegame_type: {2: 1},
                self.freegame_type: {2: 1},
            },
            "force_wincap":   True,
            "force_freegame": True,
        }

        zerowin_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
            },
            "mult_values": {
                self.basegame_type: {2: 1},
                self.freegame_type: {2: 1},
            },
            "force_wincap":   False,
            "force_freegame": False,
        }

        # ── Bet modes ─────────────────────────────────────────────────────────
        mode_maxwins = {"base": 5000, "bonus": 5000}

        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=mode_maxwins["base"],
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(criteria="wincap",   quota=0.001, win_criteria=mode_maxwins["base"], conditions=wincap_condition),
                    Distribution(criteria="freegame", quota=0.1,   conditions=freegame_condition),
                    Distribution(criteria="0",        quota=0.4,   win_criteria=0.0, conditions=zerowin_condition),
                    Distribution(criteria="basegame", quota=0.499, conditions=basegame_condition),
                ],
            ),
            BetMode(
                name="bonus",
                cost=100.0,
                rtp=self.rtp,
                max_win=mode_maxwins["bonus"],
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(criteria="wincap",   quota=0.001, win_criteria=mode_maxwins["bonus"], conditions=wincap_condition),
                    Distribution(criteria="freegame", quota=0.999, conditions=freegame_condition),
                ],
            ),
        ] 