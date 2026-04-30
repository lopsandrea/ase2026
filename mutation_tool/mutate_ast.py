"""AST-based source-level mutator (paper §4.4).

Walks an OSS subject's source tree, locates mutation targets via the
operator scanner, samples 30 unique candidates stratified across the 4
operator classes, and writes each mutant as a fresh git branch
``mutant-<subject>-<operator>-<n>`` whose only diff is the mutation.
"""
from __future__ import annotations

import argparse
import json
import random
import shutil
import subprocess
from pathlib import Path

from .operators import find_targets, apply, stratified_sample, OPERATORS

_TARGET_EXTS = {".html", ".jsx", ".js", ".vue", ".ejs", ".tsx", ".ts"}


def collect_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for path in root.rglob("*"):
        if path.suffix.lower() in _TARGET_EXTS and "node_modules" not in path.parts and ".git" not in path.parts:
            out.append(path)
    return out


def build_candidates(root: Path) -> list:
    cands = []
    for fp in collect_files(root):
        text = fp.read_text(errors="ignore")
        cands.extend(find_targets(text, fp.relative_to(root)))
    return cands


def write_mutant(*, subject: Path, mutant_id: str, cand) -> Path:
    """Materialise a mutant by checkout + diff into a fresh git branch."""
    subprocess.run(["git", "checkout", "-B", mutant_id, "main"], cwd=subject, check=False, capture_output=True)
    target = subject / cand.file
    text = target.read_text()
    text = apply(text, cand)
    target.write_text(text)
    subprocess.run(["git", "add", "-A"], cwd=subject, check=False)
    subprocess.run(["git", "commit", "-m", f"mutant {mutant_id}: {cand.operator} ({cand.description})"], cwd=subject, check=False, capture_output=True)
    subprocess.run(["git", "checkout", "main"], cwd=subject, check=False, capture_output=True)
    return target


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", type=Path, required=True, help="Path to an OSS subject (apps/<name>/)")
    ap.add_argument("--out", type=Path, default=Path("traces/rq2"))
    ap.add_argument("--per-operator", type=int, default=8)  # 8 per op ≈ 30 ± epsilon
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)

    cands = build_candidates(args.subject)
    selected = stratified_sample(cands, per_operator=args.per_operator, rng=rng)
    summary = []
    for i, cand in enumerate(selected):
        mid = f"mutant-{args.subject.name}-{cand.operator}-{i:03d}"
        write_mutant(subject=args.subject, mutant_id=mid, cand=cand)
        summary.append({
            "id": mid,
            "operator": cand.operator,
            "operator_name": OPERATORS[cand.operator],
            "file": str(cand.file),
            "span": cand.span,
            "description": cand.description,
        })

    out = args.out / f"{args.subject.name}_mutants.json"
    out.write_text(json.dumps(summary, indent=2))
    print(f"wrote {len(summary)} mutants → {out}")


if __name__ == "__main__":
    main()
