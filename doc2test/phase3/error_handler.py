"""Phase 3 — Error Handler Agent (LLM-driven, paper Tab. 3).

Receives the failure stack trace plus the freshly re-extracted DOM /
screenshot and rewrites the snippet to repair the underlying cause
(intercepted element, syntax error, etc.). Implements the bounded
ReAct repair loop of Algorithm 1.
"""
from __future__ import annotations

from typing import Any

from ..agent_base import Agent


class ErrorHandler(Agent):
    name = "error_handler"
    provider = "openai"
    model = "gpt-5-0326-2026"
    system_template = "phase3/error_handler.system.j2"
    user_template = "phase3/error_handler.user.j2"
    output_schema = "phase3_error_handler"
    accepts_images = True
    max_output_tokens = 4096
