"""SA-ReAct — Single-agent ReAct baseline (paper §4.5, Tab. 4).

A single GPT-5 instance with browser feedback access (live DOM and
screenshot at every turn) and a bounded ReAct self-healing loop M=3, but
NO role decomposition — one persona prompt encodes all responsibilities
(task extraction, DOM filtering, code synthesis, error repair).

Isolates the contribution of multi-agent decomposition from the
contribution of runtime grounding and iterative repair.
"""
from __future__ import annotations

from dataclasses import dataclass

from doc2test.llm_layer import LLMInteractionLayer
from doc2test.phase3.selenium_executor import SeleniumExecutor


@dataclass
class SaReact:
    layer: LLMInteractionLayer
    executor: SeleniumExecutor
    dom_provider: callable
    screenshot_provider: callable
    model: str = "gpt-5-0326-2026"
    max_retries: int = 3

    def run(self, *, uat_text: str) -> dict:
        history: list[dict] = []
        scratch_code = ""
        for attempt in range(self.max_retries + 1):
            dom = self.dom_provider()
            shot = self.screenshot_provider()
            ctx = {
                "uat_text": uat_text,
                "history": history,
                "live_dom": dom[:200_000],
                "previous_code": scratch_code,
            }
            raw, _, _ = self.layer.call(
                provider="openai",
                model=self.model,
                system_template="baselines/sa_react.system.j2",
                user_template="baselines/sa_react.user.j2",
                ctx=ctx,
                images=(shot,),
                max_output_tokens=8192,
            )
            scratch_code = raw.split("<code>", 1)[-1].rsplit("</code>", 1)[0].strip() if "<code>" in raw else raw.strip()
            result = self.executor.execute(scratch_code)
            history.append({"attempt": attempt, "status": result["status"], "exc": result.get("exception_type")})
            if result["status"] == "PASS":
                return {"status": "PASS", "code": scratch_code, "history": history}

        return {"status": "FAIL", "code": scratch_code, "history": history}
