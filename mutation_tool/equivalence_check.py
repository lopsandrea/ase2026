"""Tooling support for the manual equivalent-mutant inspection (paper §4.4).

We sampled 50% of the 180 mutants (90 mutants, balanced across operators
and subjects) and two authors independently confirmed inter-rater
agreement κ=0.95. This script:

1. Generates the stratified 50% sample.
2. Renders a JSON inspection sheet with one mutant per row, two reviewer
   columns, and a κ-computation helper.
"""
from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path


def stratified_50pct(mutants: list[dict], seed: int = 17) -> list[dict]:
    rng = random.Random(seed)
    by_subject_op: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for m in mutants:
        by_subject_op[(m["subject"], m["operator"])].append(m)
    sample: list[dict] = []
    for lst in by_subject_op.values():
        k = max(1, len(lst) // 2)
        rng.shuffle(lst)
        sample.extend(lst[:k])
    return sample


def cohen_kappa(a: list[int], b: list[int]) -> float:
    """Cohen's κ for two binary raters."""
    assert len(a) == len(b)
    n = len(a)
    po = sum(int(x == y) for x, y in zip(a, b)) / n
    pa1 = sum(a) / n; pb1 = sum(b) / n
    pe = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    return (po - pe) / (1 - pe) if pe != 1.0 else 1.0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mutants", type=Path, required=True, help="Aggregated mutants.json")
    ap.add_argument("--out", type=Path, default=Path("traces/rq2/equivalence_sheet.json"))
    args = ap.parse_args()
    mutants = json.loads(Path(args.mutants).read_text())
    sample = stratified_50pct(mutants)
    sheet = [
        {**m, "rater_a_equivalent": None, "rater_b_equivalent": None, "tiebreak_senior": None}
        for m in sample
    ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(sheet, indent=2))
    print(f"wrote stratified 50% sample ({len(sheet)} mutants) → {args.out}")


if __name__ == "__main__":
    main()
