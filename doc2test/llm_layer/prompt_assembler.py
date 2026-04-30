"""Jinja-based assembler for the 11 agent prompts."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined


class PromptAssembler:
    def __init__(self, templates_root: str | Path | None = None) -> None:
        if templates_root is None:
            templates_root = Path(__file__).resolve().parent.parent / "prompts"
        self.env = Environment(
            loader=FileSystemLoader(str(templates_root)),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

    def render(self, template: str, **ctx: Any) -> str:
        return self.env.get_template(template).render(**ctx)
