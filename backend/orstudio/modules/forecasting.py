from __future__ import annotations

import numpy as np
from .common import number_list, require, rounded


def _metrics(actual: list[float], predicted: list[float]) -> dict:
    if not actual:
        return {"MAD": None, "MSE": None, "RMSE": None, "MAPE": None, "n": 0}
    errors = np.asarray(actual, dtype=float) - np.asarray(predicted, dtype=float)
    abs_errors = np.abs(errors)
    nonzero = np.asarray(actual, dtype=float) != 0
    mape = float(np.mean(abs_errors[nonzero] / np.abs(np.asarray(actual)[nonzero])) * 100) if nonzero.any() else None
    return rounded({"MAD": float(abs_errors.mean()), "MSE": float(np.mean(errors ** 2)), "RMSE": float(np.sqrt(np.mean(errors ** 2))), "MAPE": mape, "n": len(actual)})


def moving_average(values, window: int = 3, horizon: int = 1) -> dict:
    y = number_list(values, "values", 2)
    require(1 <= int(window) < len(y), "window must be >= 1 and smaller than the number of observations")
    require(1 <= int(horizon) <= 120, "horizon must be between 1 and 120")
    forecasts = [float(np.mean(y[i-window:i])) for i in range(window, len(y))]
    actual = y[window:]
    history = list(y)
    future = []
    for _ in range(int(horizon)):
        next_value = float(np.mean(history[-window:]))
        future.append(next_value)
        history.append(next_value)
    return {"method": "Moving Average", "fitted": [None] * window + rounded(forecasts), "forecast": rounded(future), "metrics": _metrics(actual, forecasts), "assumptions": [f"Equal weight is assigned to the latest {window} observations."]}


def weighted_moving_average(values, weights, horizon: int = 1) -> dict:
    y = number_list(values, "values", 2)
    w = number_list(weights, "weights", 1)
    require(len(w) < len(y) + 1 and len(w) <= len(y), "weights cannot exceed the number of observations")
    weight_sum=sum(w)
    require(all(x >= 0 for x in w) and np.isfinite(weight_sum) and weight_sum > 0, "weights must be non-negative, finite in total, and have a positive sum")
    require(1 <= int(horizon) <= 120, "horizon must be between 1 and 120")
    w = np.asarray(w, dtype=float) / sum(w)
    n = len(w)
    fitted = [None] * n
    predictions = []
    for i in range(n, len(y)):
        pred = float(np.dot(np.asarray(y[i-n:i]), w))
        fitted.append(pred)
        predictions.append(pred)
    hist, future = list(y), []
    for _ in range(int(horizon)):
        pred = float(np.dot(np.asarray(hist[-n:]), w))
        future.append(pred)
        hist.append(pred)
    return {"method": "Weighted Moving Average", "weights_normalized": rounded(w.tolist()), "fitted": rounded(fitted), "forecast": rounded(future), "metrics": _metrics(y[n:], predictions), "assumptions": ["Weights are normalized to sum to 1; the last weight applies to the most recent observation."]}


def simple_exponential_smoothing(values, alpha: float = 0.3, horizon: int = 1, initial: float | None = None) -> dict:
    y = number_list(values, "values", 2)
    alpha = float(alpha)
    require(0 < alpha <= 1, "alpha must be in (0, 1]")
    require(1 <= int(horizon) <= 120, "horizon must be between 1 and 120")
    level = y[0] if initial is None else float(initial)
    require(np.isfinite(level), "initial level must be finite")
    fitted, errors = [None], []
    for value in y[1:]:
        fitted.append(level)
        errors.append(level)
        level = alpha * value + (1 - alpha) * level
    return {"method": "Simple Exponential Smoothing", "fitted": rounded(fitted), "forecast": rounded([level] * int(horizon)), "metrics": _metrics(y[1:], errors), "final_level": round(level, 6), "assumptions": ["No explicit trend or seasonality is modeled."]}


def linear_trend(values, horizon: int = 1) -> dict:
    y = number_list(values, "values", 2)
    require(1 <= int(horizon) <= 120, "horizon must be between 1 and 120")
    x = np.arange(1, len(y) + 1, dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    fitted = (intercept + slope * x).tolist()
    future_x = np.arange(len(y) + 1, len(y) + int(horizon) + 1)
    future = (intercept + slope * future_x).tolist()
    return {"method": "Linear Trend Regression", "equation": {"intercept": round(float(intercept), 6), "slope": round(float(slope), 6)}, "fitted": rounded(fitted), "forecast": rounded(future), "metrics": _metrics(y, fitted), "assumptions": ["A linear trend is extrapolated; seasonality is not modeled."]}


def naive(values, horizon: int = 1) -> dict:
    y = number_list(values, "values", 2)
    require(1 <= int(horizon) <= 120, "horizon must be between 1 and 120")
    fitted = [None] + y[:-1]
    return {"method": "Naive", "fitted": rounded(fitted), "forecast": rounded([y[-1]] * int(horizon)), "metrics": _metrics(y[1:], y[:-1]), "assumptions": ["The latest actual value is carried forward."]}


def run(params: dict) -> dict:
    method = params.get("method", "moving_average").lower()
    values = params.get("values", params.get("data", []))
    horizon = int(params.get("horizon", 1))
    if method in {"ma", "moving_average", "moving average"}:
        return moving_average(values, int(params.get("window", 3)), horizon)
    if method in {"wma", "weighted_moving_average", "weighted moving average"}:
        return weighted_moving_average(values, params.get("weights", [1, 2, 3]), horizon)
    if method in {"ses", "exponential_smoothing", "simple_exponential_smoothing"}:
        return simple_exponential_smoothing(values, float(params.get("alpha", .3)), horizon, params.get("initial"))
    if method in {"lr", "linear_regression", "linear_trend"}:
        return linear_trend(values, horizon)
    if method == "naive":
        return naive(values, horizon)
    raise ValueError(f"Unsupported forecasting method: {method}")
