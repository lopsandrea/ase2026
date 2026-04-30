"""Phase 1 / Agent 7 — Syntax Adapter (Interface Adapter)."""
from __future__ import annotations

from typing import Any

from ..agent_base import Agent


class SyntaxAdapter(Agent):
    name = "syntax_adapter"
    provider = "openai"
    model = "gpt-5-0326-2026"
    system_template = "phase1/syntax_adapter.system.j2"
    user_template = "phase1/syntax_adapter.user.j2"
    output_schema = "phase1_syntax_adapter"

    def preprocess(self, ctx: dict[str, Any]) -> dict[str, Any]:
        return {**ctx, "previous": ctx.get("context_enricher", ctx.get("previous", {}))}
