"""Phase 1 / Agent 6 — Context Enricher (Domain Expert)."""
from __future__ import annotations

from typing import Any

from ..agent_base import Agent


class ContextEnricher(Agent):
    name = "context_enricher"
    provider = "openai"
    model = "gpt-5-0326-2026"
    system_template = "phase1/context_enricher.system.j2"
    user_template = "phase1/context_enricher.user.j2"
    output_schema = "phase1_context_enricher"

    def preprocess(self, ctx: dict[str, Any]) -> dict[str, Any]:
        return {**ctx, "previous": ctx.get("logic_simplifier", ctx.get("previous", {}))}
