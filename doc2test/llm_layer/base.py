"""Provider-agnostic LLM interface (paper §3.1: LLM Interaction Layer)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class LLMRequest:
    model: str
    system: str
    user: str
    images: tuple[bytes, ...] = field(default_factory=tuple)
    temperature: float = 0.2
    top_p: float = 0.95
    max_output_tokens: int = 4096
    response_format: str = "json"  # "json" | "text"


@dataclass(frozen=True)
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int
    model: str
    cached: bool = False


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def call(self, req: LLMRequest) -> LLMResponse: ...
