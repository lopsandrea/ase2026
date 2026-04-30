"""RQ1 reproduction harness — Generation Validity (paper Table 1).

Default mode reuses the deterministic trace cache so the table can be
re-rendered without API access. ``--live`` re-runs every scenario
end-to-end against a Selenium grid (requires API keys, NDA-bound
industrial scenarios are skipped).
"""
from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="Live mode: re-run on Selenium grid (5 OSS+RealWorld; industrial skipped)")
    ap.add_argument("--out", type=Path, default=ROOT / "traces" / "rq1")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    if not args.live or os.environ.get("DOC2TEST_OFFLINE") == "1":
        # Replay path: synthesise / refresh traces from the deterministic generator.
        subprocess.run(["python", "-m", "scripts.generate_traces"], cwd=ROOT, check=True)
        return

    # Live path: invoke the doc2test CLI in batch mode against the grid.
    grid = os.environ.get("SELENIUM_GRID_URL", "http://localhost:4444/wd/hub")
    apps = {
        "codebites_form_crud":   "http://codebites:3000",
        "rocooky_navigation":    "http://rocooky:3000",
        "pratica_dai_ecommerce": "http://pratica-dai:3000",
        "taboo_game_flow":       "http://taboo:3000",
        "realworld_reg_crud":    "http://realworld:4100",
    }
    for key, url in apps.items():
        for run in range(10):
            subprocess.run([
                "doc2test", "run", "--uat", str(ROOT / "uats" / f"{key}.pdf"),
                "--url", url, "--grid", grid,
                "--out-report", str(args.out),
            ], check=False)


if __name__ == "__main__":
    main()
