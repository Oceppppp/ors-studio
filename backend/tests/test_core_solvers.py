import math

from orstudio.modules.forecasting import moving_average
from orstudio.modules.assignment import solve_assignment
from orstudio.modules.optimization import solve_linear_program
from orstudio.modules.project_management import solve_cpm
from orstudio.modules.waiting_lines import solve_mm1


def test_moving_average_returns_next_period_and_errors():
    result = moving_average([10, 12, 14, 16], window=2, horizon=1)
    assert result["forecast"] == [15.0]
    assert result["metrics"]["MAD"] == 3.0


def test_assignment_minimizes_total_cost():
    result = solve_assignment([[9, 2, 7], [6, 4, 3], [5, 8, 1]])
    assert result["assignments"] == [[0, 1], [1, 0], [2, 2]]
    assert result["objective"] == 9.0


def test_linear_program_finds_known_optimum():
    result = solve_linear_program(
        objective=[3, 5], sense="max",
        constraints=[
            {"coefficients": [1, 0], "sense": "<=", "rhs": 4},
            {"coefficients": [0, 2], "sense": "<=", "rhs": 12},
            {"coefficients": [3, 2], "sense": "<=", "rhs": 18},
        ],
        bounds=[[0, None], [0, None]],
    )
    assert result["status"] == "optimal"
    assert result["objective"] == 36.0
    assert result["variables"] == [2.0, 6.0]


def test_cpm_identifies_critical_path():
    result = solve_cpm([
        {"id": "A", "duration": 3, "predecessors": []},
        {"id": "B", "duration": 2, "predecessors": ["A"]},
        {"id": "C", "duration": 4, "predecessors": ["A"]},
        {"id": "D", "duration": 2, "predecessors": ["B", "C"]},
    ])
    assert result["project_duration"] == 9
    assert result["critical_path"] == ["A", "C", "D"]


def test_mm1_expected_metrics():
    result = solve_mm1(arrival_rate=2, service_rate=3)
    assert math.isclose(result["utilization"], 2 / 3)
    assert math.isclose(result["L"], 2)
    assert math.isclose(result["W"], 1)


def test_game_theory_mixed_strategy_is_normalized():
    from orstudio.modules.game_theory import solve_zero_sum
    result = solve_zero_sum([[1, -1], [-1, 1]])
    assert all(abs(sum(result[k]) - 1) < 1e-8 for k in ["row_player_strategy", "column_player_strategy"])
    assert abs(result["game_value"]) < 1e-8
