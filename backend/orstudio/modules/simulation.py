from __future__ import annotations

import math

import numpy as np

from .common import require


def monte_carlo(params):
    try:
        runs = int(params.get("runs", 10000))
        preview = int(params.get("preview", 20))
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("runs and preview must be integers") from exc
    require(1 <= runs <= 2_000_000, "runs must be between 1 and 2,000,000")
    require(0 <= preview <= 100, "preview must be between 0 and 100")
    seed = params.get("seed", 12345)
    try:
        rng = np.random.default_rng(seed)
    except (TypeError, ValueError) as exc:
        raise ValueError("seed must be a valid NumPy random seed") from exc
    dist = str(params.get("distribution", "normal")).lower()

    if dist == "normal":
        mean = float(params.get("mean", 0))
        sd = float(params.get("sd", 1))
        require(math.isfinite(mean) and math.isfinite(sd) and sd >= 0, "normal mean must be finite and standard deviation must be finite and non-negative")
        samples = rng.normal(mean, sd, runs)
    elif dist == "uniform":
        low = float(params.get("low", 0))
        high = float(params.get("high", 1))
        require(math.isfinite(low) and math.isfinite(high) and low < high, "uniform bounds must be finite and low < high")
        samples = rng.uniform(low, high, runs)
    elif dist == "triangular":
        left = float(params["left"])
        mode = float(params["mode"])
        right = float(params["right"])
        require(all(math.isfinite(value) for value in (left, mode, right)) and left <= mode <= right and left < right, "triangular parameters must be finite and left <= mode <= right with left < right")
        samples = rng.triangular(left, mode, right, runs)
    elif dist == "poisson":
        lam = float(params.get("lam", 1))
        require(math.isfinite(lam) and lam >= 0, "Poisson lambda must be finite and non-negative")
        samples = rng.poisson(lam, runs)
    else:
        raise ValueError("distribution must be normal, uniform, triangular, or poisson")

    ci = 1.96 * samples.std(ddof=1) / (runs ** 0.5) if runs > 1 else None
    return {
        "distribution": dist,
        "runs": runs,
        "seed": seed,
        "mean": float(samples.mean()),
        "standard_deviation": float(samples.std(ddof=1)) if runs > 1 else None,
        "median": float(np.median(samples)),
        "minimum": float(samples.min()),
        "maximum": float(samples.max()),
        "mean_95_percent_ci": [float(samples.mean() - ci), float(samples.mean() + ci)] if ci is not None else None,
        "sample_preview": samples[:preview].tolist(),
        "assumptions": ["Independent pseudorandom draws from the selected parametric distribution; confidence interval is a normal approximation for the estimated mean."],
    }
