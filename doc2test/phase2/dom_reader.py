"""Phase 2 — DOM Reader (deterministic).

Extracts the full DOM of the current page via Selenium. Re-extracted
dynamically when a page navigation or popup is detected (paper Tab. 2).
"""
from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver


class DomReader:
    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver

    def extract(self) -> str:
        return self.driver.execute_script("return document.documentElement.outerHTML;")
