"""Phase 1 / Agent 4 — Atomicity Enforcer (Step Refinement)."""
from __future__ import annotations

from typing import Any

from ..agent_base import Agent


class AtomicityEnforcer(Agent):
    name = "atomicity_enforcer"
    provider = "openai"
    model = "gpt-5-0326-2026"
    system_template = "phase1/atomicity_enforcer.system.j2"
    user_template = "phase1/atomicity_enforcer.user.j2"
    output_schema = "phase1_atomicity_enforcer"

    def preprocess(self, ctx: dict[str, Any]) -> dict[str, Any]:
        return {**ctx, "previous": ctx.get("action_concretizer", ctx.get("previous", {}))}
