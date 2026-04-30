"""SP-LLM+CoT — Enhanced single-prompt baseline (paper §4.5, Tab. 4).

Same GPT-5 instance, but with:
- DOM chunking: top-k=50 nodes ranked by tag relevance to the task,
- three few-shot Selenium examples,
- an explicit chain-of-thought instruction.

Still single-pass: no live screenshots, no self-healing.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from doc2test.llm_layer import LLMInteractionLayer

_TAG_RANK: tuple[str, ...] = (
    "input", "button", "form", "select", "textarea", "label",
    "a", "h1", "h2", "h3", "table", "tr", "td", "th", "li",
    "ul", "ol", "nav", "header", "main", "section", "article", "div",
)


def top_k_dom_nodes(html: str, *, k: int = 50) -> str:
    """Naive top-k DOM chunking by tag relevance (deterministic, baseline-safe)."""
    nodes = re.findall(r"<(\w+)[^>]*?>(?:[^<]*?)</\1>|<\w+[^/>]*/?>", html, flags=re.DOTALL)
    scored: list[tuple[int, int, str]] = []
    for m in re.finditer(r"<(\w+)[^>]*>(?:.*?</\1>|)", html, flags=re.DOTALL):
        tag = m.group(1).lower()
        try:
            rank = _TAG_RANK.index(tag)
        except ValueError:
            rank = len(_TAG_RANK)
        scored.append((rank, m.start(), m.group(0)))
    scored.sort()
    return "\n".join(s[2] for s in scored[:k])


@dataclass
class SpLlmCot:
    layer: LLMInteractionLayer
    model: str = "gpt-5-0326-2026"

    def generate(self, *, uat_text: str, html_body: str) -> str:
        chunked = top_k_dom_nodes(html_body, k=50)
        raw, _, _ = self.layer.call(
            provider="openai",
            model=self.model,
            system_template="baselines/sp_llm_cot.system.j2",
            user_template="baselines/sp_llm_cot.user.j2",
            ctx={"uat_text": uat_text, "chunked_dom": chunked},
            max_output_tokens=8192,
        )
        if "<code>" in raw and "</code>" in raw:
            return raw.split("<code>", 1)[1].rsplit("</code>", 1)[0].strip()
        return raw.strip()
