"""Phase 3 — Selenium Generator Agent (LLM-driven, paper Tab. 3).

Synthesises a Python Selenium snippet for the current task from the filtered
DOM, the screenshot (multimodal input), and the task description, with
explicit waits and a strict locator priority.
"""
from __future__ import annotations

from typing import Any

from ..agent_base import Agent


class SeleniumGenerator(Agent):
    name = "selenium_generator"
    provider = "openai"
    model = "gpt-5-0326-2026"
    system_template = "phase3/selenium_generator.system.j2"
    user_template = "phase3/selenium_generator.user.j2"
    output_schema = "phase3_selenium_generator"
    accepts_images = True
    max_output_tokens = 4096

    def preprocess(self, ctx: dict[str, Any]) -> dict[str, Any]:
        return ctx
