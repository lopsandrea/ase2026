"""Stateful transitions across the three Doc2Test phases (paper §3.2)."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Phase(str, Enum):
    REQUIREMENTS = "phase1"
    PERCEPTION = "phase2"
    GENERATION = "phase3"
    DONE = "done"
    ABORTED = "aborted"


@dataclass
class State:
    phase: Phase = Phase.REQUIREMENTS
    document_path: str = ""
    target_url: str = ""
    task_list: list[dict[str, Any]] = field(default_factory=list)
    current_task_index: int = 0
    current_task: dict[str, Any] | None = None
    current_dom_full: str = ""
    current_dom_filtered: str = ""
    current_screenshot: bytes | None = None
    current_code: str = ""
    last_error: dict[str, Any] | None = None
    attempts: int = 0
    suite: list[str] = field(default_factory=list)

    def advance_to(self, phase: Phase) -> None:
        self.phase = phase

    def reset_task_state(self) -> None:
        self.current_dom_full = ""
        self.current_dom_filtered = ""
        self.current_screenshot = None
        self.current_code = ""
        self.last_error = None
        self.attempts = 0
