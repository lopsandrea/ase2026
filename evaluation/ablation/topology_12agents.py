"""Topology ablation — Fragmented MAS (12 sub-agents).

Four of the baseline agents are split into two narrower sub-agents each,
yielding 12 total Phase-1 agents. Refer to paper §4.6 for the breakdown.
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
    print("Live topology ablation requires API keys.")


if __name__ == "__main__":
    main()
