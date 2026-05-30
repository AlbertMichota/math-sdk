from game_executables import GameExecutables


class GameStateOverride(GameExecutables):
    """
    Overrides universal state functions for Castle Fortune.
    - All Wilds are locked at 2x multiplier for line substitution
    - Quad block multipliers (10-25) are applied separately as a total win boost
    """

    def reset_book(self):
        super().reset_book()

    def assign_special_sym_function(self):
        self.special_symbol_functions = {
            "W": [self.assign_mult_property],
        }

    def assign_mult_property(self, symbol):
        """
        All Wilds are always 2x regardless of game mode.
        The quad mechanic in game_executables handles the total win
        multiplier separately — this just sets the per-symbol
        substitution value used by Lines.get_lines().
        """
        symbol.assign_attribute({"multiplier": 2})

    def check_repeat(self):
        super().check_repeat()
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True
                return
            if win_criteria is None and self.final_win == 0:
                self.repeat = True
                return