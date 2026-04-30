"""Leave-one-out component ablation (paper Table 4 panel B)."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> None:
    if os.environ.get("DOC2TEST_OFFLINE", "1") == "1":
        subprocess.run(["python", "-m", "scripts.generate_traces"], cwd=ROOT, check=True)
        return
    print("Live leave-one-out ablation requires API keys.")


if __name__ == "__main__":
    main()
