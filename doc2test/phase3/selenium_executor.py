"""Phase 3 — Selenium Executor (deterministic).

Runs the generated snippet against the live browser, captures success/failure
status and error logs, and triggers Phase-2 re-extraction on failure.
"""
from __future__ import annotations

import io
import logging
import textwrap
import traceback
from contextlib import redirect_stderr, redirect_stdout
from typing import Any

from selenium.webdriver.remote.webdriver import WebDriver

log = logging.getLogger("doc2test.executor")


class SeleniumExecutor:
    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver

    def execute(self, code: str) -> dict[str, Any]:
        """Execute the snippet inside a sandboxed namespace.

        The snippet has access to ``driver`` and the standard Selenium
        helpers. Any exception is caught and returned as a structured
        ``error_log`` so the Error Handler can repair it.
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        sandbox = {
            "driver": self.driver,
            "By": By,
            "Keys": Keys,
            "EC": EC,
            "WebDriverWait": WebDriverWait,
        }

        stdout, stderr = io.StringIO(), io.StringIO()
        normalised = textwrap.dedent(code)

        try:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exec(compile(normalised, "<doc2test.snippet>", "exec"), sandbox, sandbox)
            return {
                "status": "PASS",
                "stdout": stdout.getvalue(),
                "stderr": stderr.getvalue(),
                "exception_type": None,
                "exception_message": None,
                "traceback": None,
            }
        except Exception as exc:
            tb = traceback.format_exc()
            log.warning("snippet failed: %s", exc.__class__.__name__)
            return {
                "status": "FAIL",
                "stdout": stdout.getvalue(),
                "stderr": stderr.getvalue(),
                "exception_type": exc.__class__.__name__,
                "exception_message": str(exc),
                "traceback": tb,
            }
