"""Reusable scaffolding for the 11 LLM-driven agents (paper §3, Tables 1–3).

Every concrete agent is a thin subclass that declares:
  - ``name`` (telemetry / logging),
  - ``provider`` and ``model`` (so we honour the heterogeneous allocation of Tab. 5),
  - ``system_template`` and ``user_template`` (paths under ``doc2test/prompts/``),
  - ``output_schema`` (filename under ``doc2test/schemas/``),
  - ``preprocess`` / ``postprocess`` if needed.

The base class enforces JSON contract validation on every output so that
inter-agent communication remains structured, as required by the Coordinator
(paper §3.4 "agents do not exchange raw conversational text, but JSON payloads
strictly validated against per-agent schemas").
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, ClassVar

from .llm_layer import LLMInteractionLayer

log = logging.getLogger("doc2test.agent")


@dataclass
class AgentResult:
    name: str
    payload: dict[str, Any]
    raw: str
    input_tokens: int
    output_tokens: int
    cached: bool


class Agent:
    name: ClassVar[str] = "agent"
    provider: ClassVar[str] = "openai"
    model: ClassVar[str] = "gpt-5-0326-2026"
    system_template: ClassVar[str] = ""
    user_template: ClassVar[str] = ""
    output_schema: ClassVar[str | None] = None
    temperature: ClassVar[float] = 0.2
    top_p: ClassVar[float] = 0.95
    max_output_tokens: ClassVar[int] = 4096
    accepts_images: ClassVar[bool] = False

    def __init__(self, layer: LLMInteractionLayer) -> None:
        self.layer = layer

    def preprocess(self, ctx: dict[str, Any]) -> dict[str, Any]:
        return ctx

    def postprocess(self, payload: dict[str, Any]) -> dict[str, Any]:
        return payload

    def run(self, *, ctx: dict[str, Any], images: tuple[bytes, ...] = ()) -> AgentResult:
        ctx = self.preprocess(ctx)
        log.debug("agent=%s provider=%s model=%s", self.name, self.provider, self.model)
        raw, payload, resp = self.layer.call(
            provider=self.provider,
            model=self.model,
            system_template=self.system_template,
            user_template=self.user_template,
            ctx=ctx,
            output_schema=self.output_schema,
            images=images if self.accepts_images else (),
            temperature=self.temperature,
            top_p=self.top_p,
            max_output_tokens=self.max_output_tokens,
        )
        if payload is not None:
            payload = self.postprocess(payload)
        return AgentResult(
            name=self.name,
            payload=payload or {},
            raw=raw,
            input_tokens=resp.input_tokens,
            output_tokens=resp.output_tokens,
            cached=resp.cached,
        )
