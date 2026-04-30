"""Phase 2 — DOM Filter Agent (LLM-driven, paper Tab. 2).

The only LLM-driven component of Phase 2. Given the current atomic task and
the full DOM, autonomously decides which DOM subtrees to retain as
task-relevant and pairs them with the screenshot. The pruning is the output
of an LLM call, not a rule- or embedding-similarity heuristic.

Allocated to Gemini-2.5-pro per Tab. 5 cost breakdown.
"""
from __future__ import annotations

from typing import Any

from ..agent_base import Agent


class DomFilterAgent(Agent):
    name = "dom_filter"
    provider = "gemini"
    model = "gemini-2.5-pro-preview-03-25"
    system_template = "phase2/dom_filter.system.j2"
    user_template = "phase2/dom_filter.user.j2"
    output_schema = "phase2_dom_filter"
    accepts_images = True
    max_output_tokens = 8192

    def preprocess(self, ctx: dict[str, Any]) -> dict[str, Any]:
        ctx = dict(ctx)
        # Pre-truncate to a hard upper bound so a single page never blows
        # past the model's context window even before pruning.
        dom = ctx.get("dom", "")
        if len(dom) > 600_000:
            dom = dom[:600_000] + "\n<!-- truncated -->\n"
        ctx["dom"] = dom
        return ctx
