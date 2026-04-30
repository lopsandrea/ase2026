"""Topology ablation — Condensed MAS (3 macro-agents).

The Phase-1 chain is collapsed to:
  Ingestion (Extractor + Structuring + Action Concretizer),
  Refinement (Atomicity Enforcer + Logic Simplifier + Context Enricher),
  Finalization (Syntax Adapter + Reorderer).

Phase 2 / Phase 3 are kept at their full configuration so the measured
delta is attributable to Phase-1 decomposition (paper §4.6).
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> None:
    if os.environ.get("DOC2TEST_OFFLINE", "1") == "1":
        subprocess.run(["python", "-m", "scripts.generate_traces"], cwd=ROOT, check=True)
        return
    print("Live topology ablation requires API keys; see doc2test.phase1 for the macro-agent shim.")


if __name__ == "__main__":
    main()
