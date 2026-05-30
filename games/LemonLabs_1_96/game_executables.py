import random
from game_calculations import GameCalculations
from src.calculations.lines import Lines


class GameExecutables(GameCalculations):

    def get_block_multiplier(self, size):
        if size == 2:
            return random.randint(2, 5)
        elif size == 3:
            return random.randint(5, 10)
        elif size == 4:
            return random.randint(10, 20)
        return 2

    # ── Block detection ───────────────────────────────────────────────────────

    def _all_wilds(self, reel, row, size):
        """Check if all positions in a block of given size starting at (reel, row) are Wilds."""
        num_reels = len(self.board)
        num_rows = len(self.board[0])
        if reel + size > num_reels or row + size > num_rows:
            return False
        return all(
            self.board[r][ro].name == "W"
            for r in range(reel, reel + size)
            for ro in range(row, row + size)
        )

    def _get_block_positions(self, reel, row, size):
        """Return all (reel, row) positions in a block of given size."""
        return [
            (r, ro)
            for r in range(reel, reel + size)
            for ro in range(row, row + size)
        ]

    def find_and_grow_blocks(self):
        num_reels = len(self.board)
        # only scan visible rows, skip padding (first and last row)
        visible_rows = len(self.board[0]) - 2   # 6 - 2 = 4
        row_offset = 1                           # skip top padding row
        covered = set()
        blocks = []

        for reel in range(num_reels - 1):
            for row in range(row_offset, row_offset + visible_rows - 1):
                corners_2x2 = self._get_block_positions(reel, row, 2)
                if any(p in covered for p in corners_2x2):
                    continue
                if not self._all_wilds(reel, row, 2):
                    continue

                final_size = 2
                grew_from = [2]

                if self._all_wilds(reel, row, 3):
                    final_size = 3
                    grew_from.append(3)
                    if self._all_wilds(reel, row, 4):
                        final_size = 4
                        grew_from.append(4)

                positions = self._get_block_positions(reel, row, final_size)
                for p in positions:
                    covered.add(p)

                blocks.append({
                    "reel":       reel,
                    "row":        row,
                    "final_size": final_size,
                    "grew_from":  grew_from,
                    "positions":  positions,
                    "multiplier": self.get_block_multiplier(final_size),
                })

        return blocks, covered
    # ── Multiplier calculation ────────────────────────────────────────────────

    def calculate_total_multiplier(self, blocks, covered):
        row_offset = 1
        visible_rows = len(self.board[0]) - 2   # 4 visible rows

        single_wild_count = sum(
            1
            for reel in range(len(self.board))
            for row in range(row_offset, row_offset + visible_rows)
            if (reel, row) not in covered
            and self.board[reel][row].name == "W"
        )

        total = (single_wild_count * 2) + sum(b["multiplier"] for b in blocks)
        return total if total > 0 else 1

    # ── Event emitters ────────────────────────────────────────────────────────

    def emit_wild_blocks_event(self, blocks):
        """
        Emit one event per block with its growth sequence and final multiplier.

        Frontend uses grewFrom to animate:
          [2]       → just a 2x2 forming
          [2, 3]    → 2x2 forms, then expands to 3x3
          [2, 3, 4] → 2x2 → 3x3 → 4x4

        Event shape:
        {
          "type":       "wildBlock",
          "reel":       0,
          "row":        0,
          "grewFrom":   [2, 3],
          "finalSize":  3,
          "positions":  [[0,0],[1,0],...],
          "multiplier": 28        ← rolled from 25-35 range for 3x3
        }
        """
        for block in blocks:
            self.book.add_event({
                "type":       "wildBlock",
                "reel":       block["reel"],
                "row":        block["row"],
                "grewFrom":   block["grew_from"],
                "finalSize":  block["final_size"],
                "positions":  [[r, ro] for (r, ro) in block["positions"]],
                "multiplier": block["multiplier"],
            })

    # ── Main evaluation ───────────────────────────────────────────────────────

    def evaluate_lines_board(self):
        """Populate win-data, record wins, transmit events."""

        # 1. Find all blocks, growing each 2x2 up to its largest possible size
        blocks, covered = self.find_and_grow_blocks()

        # 2. Calculate total multiplier
        #    blocks:       final-size range rolled once per block
        #    single wilds: +2 each
        total_multiplier = self.calculate_total_multiplier(blocks, covered)

        # 3. Evaluate all 25 paylines — wilds substitute at 2x each
        self.win_data = Lines.get_lines(
            self.board, self.config, global_multiplier=self.global_multiplier
        )
        Lines.record_lines_wins(self)

        # 4. Apply total multiplier to the whole spin win
        if total_multiplier > 1:
            self.win_data["totalWin"] = self.win_data["totalWin"] * total_multiplier

        self.win_manager.update_spinwin(self.win_data["totalWin"])
        Lines.emit_linewin_events(self)

        # 5. Emit summary multiplier event so frontend can display total
        if total_multiplier > 1:
            self.book.add_event({
                "type":            "wildMultiplier",
                "totalMultiplier": total_multiplier,
            })

        # 6. Emit individual block events with growth sequences
        if blocks:
            self.emit_wild_blocks_event(blocks)