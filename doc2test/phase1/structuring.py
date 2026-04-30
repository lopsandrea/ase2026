"""Phase 1 / Agent 2 — Structuring (Schema Normalizer)."""
from __future__ import annotations

from typing import Any

from ..agent_base import Agent


class Structuring(Agent):
    name = "structuring"
    provider = "openai"
    model = "gpt-5-0326-2026"
    system_template = "phase1/structuring.system.j2"
    user_template = "phase1/structuring.user.j2"
    output_schema = "phase1_structuring"

    def preprocess(self, ctx: dict[str, Any]) -> dict[str, Any]:
        return {**ctx, "previous": ctx.get("extractor", ctx.get("previous", {}))}
