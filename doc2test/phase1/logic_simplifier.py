"""Phase 1 / Agent 5 — Logic Simplifier (Constraint Optimizer)."""
from __future__ import annotations

from typing import Any

from ..agent_base import Agent


class LogicSimplifier(Agent):
    name = "logic_simplifier"
    provider = "openai"
    model = "gpt-5-0326-2026"
    system_template = "phase1/logic_simplifier.system.j2"
    user_template = "phase1/logic_simplifier.user.j2"
    output_schema = "phase1_logic_simplifier"

    def preprocess(self, ctx: dict[str, Any]) -> dict[str, Any]:
        return {**ctx, "previous": ctx.get("atomicity_enforcer", ctx.get("previous", {}))}
