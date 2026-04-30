"""Phase 1 / Agent 3 — Action Concretizer (Functional Analyst)."""
from __future__ import annotations

from typing import Any

from ..agent_base import Agent


class ActionConcretizer(Agent):
    name = "action_concretizer"
    provider = "openai"
    model = "gpt-5-0326-2026"
    system_template = "phase1/action_concretizer.system.j2"
    user_template = "phase1/action_concretizer.user.j2"
    output_schema = "phase1_action_concretizer"

    def preprocess(self, ctx: dict[str, Any]) -> dict[str, Any]:
        return {**ctx, "previous": ctx.get("structuring", ctx.get("previous", {}))}
