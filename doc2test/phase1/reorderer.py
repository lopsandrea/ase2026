"""Phase 1 / Agent 8 — Reorderer (Logic Validator).

Final emitter of the canonical ``tasks`` list consumed by Phase 2 / Phase 3.
"""
from __future__ import annotations

from typing import Any

from ..agent_base import Agent


class Reorderer(Agent):
    name = "reorderer"
    provider = "openai"
    model = "gpt-5-0326-2026"
    system_template = "phase1/reorderer.system.j2"
    user_template = "phase1/reorderer.user.j2"
    output_schema = "phase1_reorderer"

    def preprocess(self, ctx: dict[str, Any]) -> dict[str, Any]:
        return {**ctx, "previous": ctx.get("syntax_adapter", ctx.get("previous", {}))}
