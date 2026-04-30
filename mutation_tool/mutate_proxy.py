"""Runtime DOM-mutation proxy (paper §4.4, NDA-bound industrial app).

Injects mutations into the live DOM via Chrome DevTools Protocol during
test execution, so we can mutate the production application without
modifying its source code (NDA constraint).

This module is provided for completeness/parity with the AST-based
mutator. The actual industrial mutants used in Tab. 2 were obtained
during the live deployment loop; the corresponding outcomes are stored
under ``traces/industrial_redacted/rq2/`` and replayed by the
evaluation harness without re-running the proxy.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from selenium.webdriver.remote.webdriver import WebDriver

from .operators import (
    ATTRIBUTE_MODIFICATION,
    ELEMENT_REMOVAL,
    EVENT_HANDLER_DETACHMENT,
    STATE_LOGIC_INVERSION,
)

_INJECTORS: dict[str, str] = {
    ELEMENT_REMOVAL: """
        (selector) => {
          const el = document.querySelector(selector);
          if (el) el.remove();
        }
    """,
    ATTRIBUTE_MODIFICATION: """
        (selector, attr, oldValue, newValue) => {
          const el = document.querySelector(selector);
          if (el && el.getAttribute(attr) === oldValue) el.setAttribute(attr, newValue);
        }
    """,
    STATE_LOGIC_INVERSION: """
        (selector) => {
          const el = document.querySelector(selector);
          if (!el) return;
          if (el.disabled !== undefined) el.disabled = !el.disabled;
          else if (el.hidden !== undefined) el.hidden = !el.hidden;
        }
    """,
    EVENT_HANDLER_DETACHMENT: """
        (selector, event) => {
          const el = document.querySelector(selector);
          if (el) el['on' + event] = null;
        }
    """,
}


@dataclass
class RuntimeMutation:
    operator: str
    selector: str
    extra: dict


def inject(driver: WebDriver, mutation: RuntimeMutation) -> None:
    fn = _INJECTORS[mutation.operator]
    args: list = [mutation.selector]
    if mutation.operator == ATTRIBUTE_MODIFICATION:
        args += [mutation.extra["attr"], mutation.extra["oldValue"], mutation.extra["newValue"]]
    elif mutation.operator == EVENT_HANDLER_DETACHMENT:
        args.append(mutation.extra.get("event", "click"))
    driver.execute_script(f"({fn})(...arguments);", *args)
