"""NDA-aware audit of industrial traces.

Scans every JSON file under ``traces/industrial_redacted/`` for any
identifier that should never have left the client's perimeter. Fails
closed: any leak aborts with a non-zero exit code.

The deny-list is encoded here rather than read from a file so a
reviewer can verify it with one ``cat`` invocation. We do **not** name
the client or its products in this list — instead we ban every concrete
substitute placeholder we know we should be using.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "traces" / "industrial_redacted"

REQUIRED_PLACEHOLDERS = (
    "[CLIENT_URL]", "[CLIENT_STAGING_URL]", "[CLIENT]",
    "[CRUISE_COMPANY_X]", "[SHIP_X]", "[ITINERARY_ID]",
    "[CABIN_TYPE]", "[BOOKING_ID]", "[QA_AGENT_USER]",
    "[QA_AGENT_PASS]", "[AGENT_USER]", "[AGENT_PASS]",
)

FORBIDDEN_PATTERNS = (
    re.compile(r"\b(MSC|Costa|Royal Caribbean|Norwegian|Carnival)\b", re.I),
    re.compile(r"\bbooking-?id\s*[:=]\s*[A-Z]{3,}\d{4,}\b"),
    re.compile(r"itinerary-?id\s*[:=]\s*\d{6,}", re.I),
    re.compile(r"@(?:wideverse-internal|client-private)\.[a-z]+", re.I),
)


def scan() -> int:
    leaks: list[tuple[Path, str]] = []
    for path in TARGET.rglob("*.json"):
        text = path.read_text()
        for pat in FORBIDDEN_PATTERNS:
            for m in pat.finditer(text):
                leaks.append((path, m.group(0)))
    if leaks:
        print("FAIL: redaction violations detected")
        for path, hit in leaks:
            print(f"  {path.relative_to(ROOT)}: {hit!r}")
        return 1
    print(f"OK: {len(list(TARGET.rglob('*.json')))} industrial trace files scanned, no leaks.")
    return 0


if __name__ == "__main__":
    sys.exit(scan())
