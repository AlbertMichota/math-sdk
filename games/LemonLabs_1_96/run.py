"""Main file for generating results for sample lines-pay game."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from optimization_program.optimization_config import (
    ConstructScaling,
    ConstructParameters,
    ConstructConditions,
    ConstructFenceBias,
    verify_optimization_input,
)
from gamestate import GameState
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":

    num_threads = 10
    rust_threads = 20
    batching_size = 500
    compression = False
    profiling = False

    num_sim_args = {
        "base": 10000,
        "bonus": 10000,
    }

    run_conditions = {
        "run_sims": True,
        "run_optimization": True,   # turn back on
        "run_analysis": False,
        "run_format_checks": False,
    }

    target_modes = list(num_sim_args.keys())
    config = GameConfig()
    gamestate = GameState(config)

    if run_conditions["run_optimization"]:
        optimization_setup_class = OptimizationSetup(config)

    if run_conditions["run_sims"]:
        create_books(
            gamestate,
            config,
            num_sim_args,
            batching_size,
            num_threads,
            compression,
            profiling,
        )

    generate_configs(gamestate)

    if run_conditions["run_optimization"]:
        OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
        generate_configs(gamestate)

