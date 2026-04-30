"""OpenAI provider for GPT-5 (Phase 1 + Phase 3, paper Tab. 5)."""
from __future__ import annotations

import base64
import os

from .base import LLMProvider, LLMRequest, LLMResponse


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, api_key: str | None = None) -> None:
        from openai import OpenAI  # local import: lib optional in offline mode

        self._client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))

    def call(self, req: LLMRequest) -> LLMResponse:
        content: list[dict] = [{"type": "text", "text": req.user}]
        for img in req.images:
            b64 = base64.b64encode(img).decode()
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{b64}"},
            })

        kwargs: dict = dict(
            model=req.model,
            messages=[
                {"role": "system", "content": req.system},
                {"role": "user", "content": content},
            ],
            temperature=req.temperature,
            top_p=req.top_p,
            max_tokens=req.max_output_tokens,
        )
        if req.response_format == "json":
            kwargs["response_format"] = {"type": "json_object"}

        resp = self._client.chat.completions.create(**kwargs)
        usage = resp.usage
        return LLMResponse(
            text=resp.choices[0].message.content or "",
            input_tokens=getattr(usage, "prompt_tokens", 0),
            output_tokens=getattr(usage, "completion_tokens", 0),
            model=req.model,
        )
