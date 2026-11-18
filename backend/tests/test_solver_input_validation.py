import pytest


def test_decision_analysis_rejects_nan_and_matrix_probabilities():
    from orstudio.modules.decision_analysis import solve_decision_analysis

    with pytest.raises(ValueError, match="probabilities"):
        solve_decision_analysis([[1, 2], [3, 4]], [float("nan"), float("nan")])
    with pytest.raises(ValueError, match="probabilities"):
        solve_decision_analysis([[1, 2], [3, 4]], [[0.5, 0.5]])


def test_capital_investment_rejects_non_finite_cash_flows():
    from orstudio.modules.finance import solve_capital_investment

    with pytest.raises(ValueError, match="finite"):
        solve_capital_investment(100, [float("inf"), 120], 0.1)


def test_network_algorithms_reject_non_finite_costs_and_capacities():
    from orstudio.modules.networks import shortest_path, maximum_flow

    with pytest.raises(ValueError, match="finite"):
        shortest_path(["A", "B"], [{"from": "A", "to": "B", "cost": float("inf")}], "A", "B")
    with pytest.raises(ValueError, match="finite"):
        maximum_flow(["A", "B"], [{"from": "A", "to": "B", "capacity": float("nan")}], "A", "B")


def test_transportation_rejects_empty_problem():
    from orstudio.modules.transportation import solve_transportation

    with pytest.raises(ValueError, match="non-empty"):
        solve_transportation([], [], [])


def test_monte_carlo_validates_distribution_parameters_and_preview():
    from orstudio.modules.simulation import monte_carlo

    with pytest.raises(ValueError, match="standard deviation"):
        monte_carlo({"distribution": "normal", "sd": -1, "runs": 100})
    with pytest.raises(ValueError, match="preview"):
        monte_carlo({"distribution": "uniform", "preview": -2, "runs": 100})
    with pytest.raises(ValueError, match="triangular"):
        monte_carlo({"distribution": "triangular", "left": 5, "mode": 2, "right": 1, "runs": 100})


def test_mrp_rejects_negative_or_non_finite_requirements():
    from orstudio.modules.mrp import solve_mrp

    with pytest.raises(ValueError, match="MPS values"):
        solve_mrp({"P": [1, float("nan")]}, {})
    with pytest.raises(ValueError, match="scheduled receipts"):
        solve_mrp({"P": [1, 2]}, {}, scheduled_receipts={"P": [0, -1]})


def test_inventory_and_queue_models_reject_non_finite_rates():
    from orstudio.modules.inventory import solve_inventory
    from orstudio.modules.waiting_lines import solve_mm1

    with pytest.raises(ValueError, match="finite"):
        solve_inventory({"model": "eoq", "annual_demand": float("inf"), "ordering_cost": 10, "holding_cost": 2})
    with pytest.raises(ValueError, match="finite"):
        solve_mm1(float("nan"), 4)


def test_quality_charts_validate_control_constants_and_sigma():
    from orstudio.modules.quality import xbar_r_chart, p_chart

    with pytest.raises(ValueError, match="constants"):
        xbar_r_chart([[1, 2], [2, 3]], A2=float("nan"), D3=0, D4=3)
    with pytest.raises(ValueError, match="sigma"):
        p_chart([1, 2], [10, 10], sigma=float("nan"))


def test_markov_rejects_invalid_initial_probability_vector():
    from orstudio.modules.markov import solve_markov

    with pytest.raises(ValueError, match="initial_state"):
        solve_markov([[0.8, 0.2], [0.1, 0.9]], [float("nan"), float("nan")])


def test_layout_rejects_unsupported_distance_metric():
    from orstudio.modules.operations import evaluate_layout

    with pytest.raises(ValueError, match="distance"):
        evaluate_layout([{"id": "A", "x": 0, "y": 0}], [], distance="road-network")


def test_linear_program_rejects_non_finite_constraint_and_invalid_bounds():
    from orstudio.modules.optimization import solve_linear_program

    with pytest.raises(ValueError, match="finite coefficients"):
        solve_linear_program([1], [{"coefficients": [float("nan")], "sense": "<=", "rhs": 1}])
    with pytest.raises(ValueError, match="lower bound exceeds upper"):
        solve_linear_program([1], [], bounds=[[5, 2]])


def test_integer_program_rejects_fractional_integrality_codes():
    from orstudio.modules.optimization import solve_integer_program

    with pytest.raises(ValueError, match="integrality"):
        solve_integer_program([1], [], integrality=[0.5])


def test_forecasting_rejects_non_finite_smoothing_initial_and_weight_sum():
    from orstudio.modules.forecasting import simple_exponential_smoothing, weighted_moving_average

    with pytest.raises(ValueError, match="initial level"):
        simple_exponential_smoothing([1, 2, 3], initial=float("inf"))
    with pytest.raises(ValueError, match="positive sum"):
        weighted_moving_average([1, 2, 3], [1e308, 1e308])


def test_forecast_comparison_rejects_non_finite_observations(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from orstudio.api import app

    monkeypatch.setenv("ORS_DATA_DIR", str(tmp_path))
    with TestClient(app) as client:
        response = client.post("/api/forecast/compare", content='{"values":[1,2,3,4,NaN,6]}', headers={"Content-Type": "application/json"})
        assert response.status_code == 400
        assert "finite" in response.json()["detail"]


def test_pert_uses_variance_of_one_complete_critical_path_not_union_of_activities():
    from orstudio.modules.project_management import solve_pert

    result = solve_pert([
        {"id": "A", "optimistic": 1, "most_likely": 1, "pessimistic": 1, "predecessors": []},
        {"id": "B", "optimistic": 1, "most_likely": 2, "pessimistic": 3, "predecessors": ["A"]},
        {"id": "C", "optimistic": 0, "most_likely": 2, "pessimistic": 4, "predecessors": ["A"]},
        {"id": "D", "optimistic": 1, "most_likely": 1, "pessimistic": 1, "predecessors": ["B", "C"]},
    ])
    assert result["critical_activities"] == ["A", "B", "C", "D"]
    assert result["representative_critical_path"] == ["A", "B", "D"]
    assert abs(result["critical_path_variance"] - (1 / 9)) < 1e-8


def test_eoq_rejects_zero_ordering_cost_instead_of_dividing_by_zero():
    from orstudio.modules.inventory import solve_inventory

    with pytest.raises(ValueError, match="ordering_cost must be > 0"):
        solve_inventory({"model": "eoq", "annual_demand": 1000, "ordering_cost": 0, "holding_cost": 2})
