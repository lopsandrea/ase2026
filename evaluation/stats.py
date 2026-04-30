"""Statistical helpers used by the reproduction harness.

Wilson 95% binomial CI for SR aggregates, Cohen's κ for inter-rater
agreement, and the mean ± σ helper used in every result table.
"""
from __future__ import annotations

import math
from typing import Iterable


def wilson_interval(successes: int, n: int, *, z: float = 1.959963984540054) -> tuple[float, float]:
    """Wilson 95% binomial CI (paper §4.3, "94.4% (95% CI [87.5%, 98.2%])")."""
    if n == 0:
        return (0.0, 0.0)
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def cohen_kappa_binary(a: Iterable[int], b: Iterable[int]) -> float:
    a, b = list(a), list(b)
    assert len(a) == len(b)
    n = len(a) or 1
    po = sum(int(x == y) for x, y in zip(a, b)) / n
    pa1, pb1 = sum(a) / n, sum(b) / n
    pe = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    return (po - pe) / (1 - pe) if pe != 1.0 else 1.0


def mean_std(values: Iterable[float]) -> tuple[float, float]:
    xs = list(values)
    if not xs:
        return (0.0, 0.0)
    mean = sum(xs) / len(xs)
    var = sum((x - mean) ** 2 for x in xs) / len(xs)
    return (mean, math.sqrt(var))


def fmt_mean_std(values: Iterable[float], *, fmt: str = "{:.1f}") -> str:
    m, s = mean_std(values)
    return f"{fmt.format(m)} ± {fmt.format(s)}"
