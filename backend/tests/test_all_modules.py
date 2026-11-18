import json

from orstudio.api import clean_json
from orstudio.registry import MODULES, run_module


def test_every_baseline_module_has_a_working_default_example():
    assert len(MODULES) == 29
    failures = []
    for module in MODULES:
        try:
            result = run_module(module["key"], module["default_params"])
            assert isinstance(result, dict) and result, f"{module['key']} returned no result"
            json.dumps(clean_json(result), ensure_ascii=False, allow_nan=False)
        except Exception as exc:
            failures.append(f"{module['key']}: {type(exc).__name__}: {exc}")
    assert not failures, "\n".join(failures)


def test_game_theory_strategy_probabilities_are_valid():
    from orstudio.modules.game_theory import solve_zero_sum
    result = solve_zero_sum([[3, 1], [0, 2]])
    assert abs(sum(result['row_player_strategy']) - 1) < 1e-8
    assert abs(sum(result['column_player_strategy']) - 1) < 1e-8
    assert abs(result['game_value'] - 1.5) < 1e-8
