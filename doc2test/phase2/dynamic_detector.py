"""Phase 2 — Dynamic Element Detector (deterministic).

Detects transient components (modals, spinners, animations) and triggers
re-extraction until the UI state is stable. Implements the stability check
referenced in Algorithm 1 lines 8–11 (paper §3.2).
"""
from __future__ import annotations

import time

from selenium.webdriver.remote.webdriver import WebDriver

# Heuristic CSS selectors capturing the most common transient overlays.
_TRANSIENT_SELECTORS = (
    ".loading", ".spinner", ".loader", "[aria-busy='true']",
    ".modal.show", ".overlay", ".cookie-banner", ".toast",
    ".mat-progress-spinner", ".mat-progress-bar", "ngx-spinner",
)


class DynamicElementDetector:
    def __init__(
        self,
        driver: WebDriver,
        *,
        max_wait_seconds: float = 8.0,
        poll_interval: float = 0.25,
    ) -> None:
        self.driver = driver
        self.max_wait = max_wait_seconds
        self.poll_interval = poll_interval

    def is_dynamic(self, dom: str, screenshot: bytes) -> bool:
        return self._has_transient(dom) or self._document_not_ready()

    def wait_for_stability(self) -> None:
        deadline = time.time() + self.max_wait
        while time.time() < deadline:
            dom = self.driver.execute_script("return document.documentElement.outerHTML;")
            if not self._has_transient(dom) and not self._document_not_ready():
                return
            time.sleep(self.poll_interval)

    def _has_transient(self, dom: str) -> bool:
        return any(sel.lstrip(".[") in dom for sel in _TRANSIENT_SELECTORS)

    def _document_not_ready(self) -> bool:
        try:
            return self.driver.execute_script("return document.readyState;") != "complete"
        except Exception:
            return False
