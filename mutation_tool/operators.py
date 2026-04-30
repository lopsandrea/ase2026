"""4 mutation operators (paper §4.4, taxonomy from Mansour & Houri 2006)."""
from __future__ import annotations

import re
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

ELEMENT_REMOVAL = "ER"
ATTRIBUTE_MODIFICATION = "AM"
STATE_LOGIC_INVERSION = "SLI"
EVENT_HANDLER_DETACHMENT = "EHD"


@dataclass
class MutationCandidate:
    operator: str
    file: Path
    span: tuple[int, int]      # (start, end) byte offsets in original file
    original: str
    mutated: str
    description: str


def find_targets(source: str, file: Path) -> list[MutationCandidate]:
    cands: list[MutationCandidate] = []

    # ER — delete a button / input / a / form tag (one element, balanced).
    for m in re.finditer(r"<(button|input|a|form|select)\b[^>]*>.*?</\1>|<(button|input|a|select)\b[^>]*/?>", source, flags=re.DOTALL):
        cands.append(MutationCandidate(
            operator=ELEMENT_REMOVAL, file=file, span=(m.start(), m.end()),
            original=m.group(0), mutated="<!-- ER mutation: element removed -->",
            description="Delete a functional UI component from the DOM",
        ))

    # AM — change an id/name/class attribute value.
    for m in re.finditer(r'\b(id|name|class|data-test-id)="([^"]+)"', source):
        attr, val = m.group(1), m.group(2)
        cands.append(MutationCandidate(
            operator=ATTRIBUTE_MODIFICATION, file=file, span=(m.start(), m.end()),
            original=m.group(0), mutated=f'{attr}="{val}-am-mut"',
            description=f"Change critical identifier ({attr}) used by selectors",
        ))

    # SLI — flip a state attribute (disabled<->enabled, hidden<->visible).
    for m in re.finditer(r'\b(disabled|hidden|readonly|checked)\b', source):
        cands.append(MutationCandidate(
            operator=STATE_LOGIC_INVERSION, file=file, span=(m.start(), m.end()),
            original=m.group(0), mutated=f"{m.group(0)}-flipped",
            description="Invert initial/conditional state of a component",
        ))
    # Or inject a `disabled` attribute onto an enabled button.
    for m in re.finditer(r'<button\b([^>]*?)>', source):
        if "disabled" not in m.group(1):
            cands.append(MutationCandidate(
                operator=STATE_LOGIC_INVERSION, file=file, span=(m.start(), m.end()),
                original=m.group(0), mutated=m.group(0)[:-1] + " disabled>",
                description="Render a button as disabled despite valid input",
            ))

    # EHD — detach onClick / onSubmit / @click / v-on / React handler.
    for m in re.finditer(r'\b(onClick|onSubmit|onChange|@click|@submit|v-on:click)\s*=\s*\{[^}]*\}', source):
        cands.append(MutationCandidate(
            operator=EVENT_HANDLER_DETACHMENT, file=file, span=(m.start(), m.end()),
            original=m.group(0), mutated="",
            description="Remove the event handler so the UI is unresponsive",
        ))
    for m in re.finditer(r'\b(onclick|onsubmit|onchange)\s*=\s*"[^"]*"', source):
        cands.append(MutationCandidate(
            operator=EVENT_HANDLER_DETACHMENT, file=file, span=(m.start(), m.end()),
            original=m.group(0), mutated="",
            description="Remove the inline DOM event handler",
        ))

    return cands


def apply(source: str, cand: MutationCandidate) -> str:
    return source[: cand.span[0]] + cand.mutated + source[cand.span[1] :]


OPERATORS: dict[str, str] = {
    ELEMENT_REMOVAL: "Element Removal",
    ATTRIBUTE_MODIFICATION: "Attribute Modification",
    STATE_LOGIC_INVERSION: "State Logic Inversion",
    EVENT_HANDLER_DETACHMENT: "Event Handler Detachment",
}


def stratified_sample(
    candidates: list[MutationCandidate],
    *,
    per_operator: int,
    rng: random.Random | None = None,
) -> list[MutationCandidate]:
    """Sample ``per_operator`` candidates per mutation class (paper §4.4)."""
    rng = rng or random.Random(42)
    by_op: dict[str, list[MutationCandidate]] = {}
    for c in candidates:
        by_op.setdefault(c.operator, []).append(c)
    chosen: list[MutationCandidate] = []
    for op, lst in by_op.items():
        rng.shuffle(lst)
        chosen.extend(lst[:per_operator])
    return chosen
