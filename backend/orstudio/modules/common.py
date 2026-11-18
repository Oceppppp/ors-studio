from __future__ import annotations

import math
from typing import Any, Iterable


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def finite_number(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a number") from exc
    require(math.isfinite(number), f"{label} must be finite")
    return number


def number_list(values: Iterable[Any], label: str, minimum: int = 1) -> list[float]:
    result = [finite_number(v, f"{label}[{i}]") for i, v in enumerate(values)]
    require(len(result) >= minimum, f"{label} must contain at least {minimum} value(s)")
    return result


def rounded(value: Any, digits: int = 6) -> Any:
    if isinstance(value, float):
        return round(value, digits) if math.isfinite(value) else None
    if isinstance(value, list):
        return [rounded(x, digits) for x in value]
    if isinstance(value, tuple):
        return [rounded(x, digits) for x in value]
    if isinstance(value, dict):
        return {k: rounded(v, digits) for k, v in value.items()}
    return value
