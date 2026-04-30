"""SP-LLM — Zero-shot single-prompt baseline (paper §4.5, Tab. 4).

A single GPT-5 instance receives the raw PDF text and the complete,
unfiltered static HTML body and must generate the full Selenium script in
one shot, without visual feedback or self-healing.
"""
from __future__ import annotations

from dataclasses import dataclass

from doc2test.llm_layer import LLMInteractionLayer

PROMPT = """\
You are an expert Selenium 4 engineer. Read the UAT document below and the
full HTML body of the application under test, and emit a single Python
Selenium script that automates the entire user journey end-to-end. Use
explicit waits and never call ``time.sleep``. The script will be executed
in a sandbox where ``driver``, ``By``, ``Keys``, ``EC`` and
``WebDriverWait`` are pre-imported.

## UAT document

{uat_text}

## Application HTML body

```html
{html_body}
```

Emit ONLY the Python source between ``<code>`` and ``</code>`` markers.
"""


@dataclass
class SpLlm:
    layer: LLMInteractionLayer
    model: str = "gpt-5-0326-2026"

    def generate(self, *, uat_text: str, html_body: str) -> str:
        raw, _, _ = self.layer.call(
            provider="openai",
            model=self.model,
            system_template="baselines/sp_llm.system.j2",
            user_template="baselines/sp_llm.user.j2",
            ctx={"uat_text": uat_text, "html_body": html_body},
            max_output_tokens=8192,
        )
        return _extract_code(raw)


def _extract_code(raw: str) -> str:
    if "<code>" in raw and "</code>" in raw:
        return raw.split("<code>", 1)[1].rsplit("</code>", 1)[0].strip()
    return raw.strip()
