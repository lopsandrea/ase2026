"""Top-level facade that mediates every agent ↔ provider exchange.

Encapsulates: prompt assembly, schema validation, cache lookup,
provider invocation, exponential-backoff retry. The internal logic of each
agent is decoupled from the underlying provider (paper §3.1).
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential

from .base import LLMProvider, LLMRequest, LLMResponse
from .cache import DiskCache
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .prompt_assembler import PromptAssembler
from .schema_validator import SchemaValidator

log = logging.getLogger(__name__)


@dataclass
class CallStats:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_hits: int = 0
    api_calls: int = 0
    retries: int = 0


@dataclass
class LLMInteractionLayer:
    cache: DiskCache = field(default_factory=DiskCache)
    assembler: PromptAssembler = field(default_factory=PromptAssembler)
    validator: SchemaValidator = field(default_factory=SchemaValidator)
    providers: dict[str, LLMProvider] = field(default_factory=dict)
    stats: CallStats = field(default_factory=CallStats)
    offline: bool = field(default_factory=lambda: os.environ.get("DOC2TEST_OFFLINE") == "1")

    def __post_init__(self) -> None:
        if not self.providers:
            self.providers = {}
            if not self.offline and os.environ.get("OPENAI_API_KEY"):
                self.providers["openai"] = OpenAIProvider()
            if not self.offline and os.environ.get("GEMINI_API_KEY"):
                self.providers["gemini"] = GeminiProvider()

    def call(
        self,
        *,
        provider: str,
        model: str,
        system_template: str,
        user_template: str,
        ctx: dict[str, Any],
        output_schema: str | None = None,
        images: tuple[bytes, ...] = (),
        temperature: float = 0.2,
        top_p: float = 0.95,
        max_output_tokens: int = 4096,
    ) -> tuple[str, dict[str, Any] | None, LLMResponse]:
        system = self.assembler.render(system_template, **ctx)
        user = self.assembler.render(user_template, **ctx)
        req = LLMRequest(
            model=model,
            system=system,
            user=user,
            images=images,
            temperature=temperature,
            top_p=top_p,
            max_output_tokens=max_output_tokens,
            response_format="json" if output_schema else "text",
        )

        cached = self.cache.get(req)
        if cached is not None:
            self.stats.cache_hits += 1
            self.stats.input_tokens += cached.input_tokens
            self.stats.output_tokens += cached.output_tokens
            payload = self.validator.parse_and_validate(output_schema, cached.text) if output_schema else None
            return cached.text, payload, cached

        if self.offline:
            raise RuntimeError(
                f"Offline mode but no cached response for prompt {system_template} (key={self.cache.key(req)[:12]})"
            )

        if provider not in self.providers:
            raise RuntimeError(f"Provider '{provider}' not configured")

        resp = self._invoke_with_retry(self.providers[provider], req)
        self.stats.api_calls += 1
        self.stats.input_tokens += resp.input_tokens
        self.stats.output_tokens += resp.output_tokens
        self.cache.put(req, resp)

        payload = self.validator.parse_and_validate(output_schema, resp.text) if output_schema else None
        return resp.text, payload, resp

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=8))
    def _invoke_with_retry(self, provider: LLMProvider, req: LLMRequest) -> LLMResponse:
        return provider.call(req)
