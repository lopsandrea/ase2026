"""RQ3 reproduction harness — comparative analysis (paper Table 3)."""
from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()
    if not args.live or os.environ.get("DOC2TEST_OFFLINE") == "1":
        subprocess.run(["python", "-m", "scripts.generate_traces"], cwd=ROOT, check=True)
        return
    print("Live RQ3 baselines re-run is gated by API keys; see baselines/* modules.")


if __name__ == "__main__":
    main()
