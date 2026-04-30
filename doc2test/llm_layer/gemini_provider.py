"""Gemini-2.5-pro provider (Phase 2 DOM Filter Agent, paper Tab. 5)."""
from __future__ import annotations

import os

from .base import LLMProvider, LLMRequest, LLMResponse


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self, api_key: str | None = None) -> None:
        import google.generativeai as genai

        genai.configure(api_key=api_key or os.environ.get("GEMINI_API_KEY"))
        self._genai = genai

    def call(self, req: LLMRequest) -> LLMResponse:
        from google.generativeai import GenerationConfig

        model = self._genai.GenerativeModel(
            req.model,
            system_instruction=req.system,
            generation_config=GenerationConfig(
                temperature=req.temperature,
                top_p=req.top_p,
                max_output_tokens=req.max_output_tokens,
                response_mime_type="application/json" if req.response_format == "json" else "text/plain",
            ),
        )
        parts: list = [req.user]
        for img in req.images:
            parts.append({"mime_type": "image/png", "data": img})

        resp = model.generate_content(parts)
        usage = resp.usage_metadata
        return LLMResponse(
            text=resp.text,
            input_tokens=getattr(usage, "prompt_token_count", 0),
            output_tokens=getattr(usage, "candidates_token_count", 0),
            model=req.model,
        )
