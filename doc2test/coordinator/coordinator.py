"""Doc2Test Coordinator — implementation of Algorithm 1 (paper §3.2)."""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..llm_layer import LLMInteractionLayer
from .state_machine import Phase, State

log = logging.getLogger("doc2test.coordinator")


class AbortError(RuntimeError):
    """Unrecoverable failure on a task — surfaced rather than silently retried."""


@dataclass
class RunReport:
    document: str
    target_url: str
    tasks: list[dict[str, Any]] = field(default_factory=list)
    suite: list[str] = field(default_factory=list)
    status: str = "PENDING"
    aborted_on_task: dict[str, Any] | None = None
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_retries: int = 0
    elapsed_seconds: float = 0.0
    per_task_metrics: list[dict[str, Any]] = field(default_factory=list)


class Coordinator:
    """Stateful orchestrator: Phase 1 (chain) → loop over Phase 2/3 per task."""

    def __init__(
        self,
        *,
        layer: LLMInteractionLayer,
        phase1_chain: list,
        dom_reader,
        screenshot_acquirer,
        dynamic_detector,
        dom_filter_agent,
        selenium_generator,
        selenium_executor,
        error_handler,
        max_retries: int = 3,
    ) -> None:
        self.layer = layer
        self.phase1_chain = phase1_chain
        self.dom_reader = dom_reader
        self.screenshot_acquirer = screenshot_acquirer
        self.dynamic_detector = dynamic_detector
        self.dom_filter_agent = dom_filter_agent
        self.selenium_generator = selenium_generator
        self.selenium_executor = selenium_executor
        self.error_handler = error_handler
        self.max_retries = max_retries

    # ------------------------------------------------------------------ public API

    def run(self, *, document: str | Path, target_url: str) -> RunReport:
        state = State(document_path=str(document), target_url=target_url)
        report = RunReport(document=str(document), target_url=target_url)
        t0 = time.perf_counter()

        try:
            self._phase1_analyze_requirements(state, report)
            self._phase23_loop(state, report)
            report.status = "PASS"
        except AbortError as exc:
            state.advance_to(Phase.ABORTED)
            report.status = "ABORTED"
            report.aborted_on_task = state.current_task
            log.error("aborted: %s", exc)
        finally:
            report.elapsed_seconds = time.perf_counter() - t0
            report.total_input_tokens = self.layer.stats.input_tokens
            report.total_output_tokens = self.layer.stats.output_tokens

        return report

    # --------------------------------------------------------- phase 1: requirements

    def _phase1_analyze_requirements(self, state: State, report: RunReport) -> None:
        """L ← AnalyzeRequirements(D) — Phase 1 agent chain (Tab. 1)."""
        log.info("phase 1: analyze requirements")
        state.advance_to(Phase.REQUIREMENTS)

        ctx: dict[str, Any] = {"document_path": state.document_path}
        for agent in self.phase1_chain:
            log.info("  → %s", agent.name)
            result = agent.run(ctx=ctx)
            ctx[agent.name] = result.payload
            ctx["previous"] = result.payload

        state.task_list = ctx["previous"].get("tasks", [])
        report.tasks = state.task_list
        log.info("phase 1: %d atomic tasks emitted", len(state.task_list))

    # -------------------------------------------------- phase 2/3: per-task loop

    def _phase23_loop(self, state: State, report: RunReport) -> None:
        for idx, task in enumerate(state.task_list):
            state.current_task_index = idx
            state.current_task = task
            state.reset_task_state()

            metric = {
                "task_index": idx,
                "task_id": task.get("id", f"task-{idx}"),
                "attempts": 0,
                "status": "PENDING",
            }

            success = False
            while not success and state.attempts < self.max_retries:
                # Phase 2 — Dynamic Context Perception
                state.advance_to(Phase.PERCEPTION)
                dom = self.dom_reader.extract()
                shot = self.screenshot_acquirer.capture()
                if self.dynamic_detector.is_dynamic(dom, shot):
                    self.dynamic_detector.wait_for_stability()
                    dom = self.dom_reader.extract()
                    shot = self.screenshot_acquirer.capture()
                state.current_dom_full = dom
                state.current_screenshot = shot

                filter_result = self.dom_filter_agent.run(
                    ctx={"task": task, "dom": dom},
                    images=(shot,),
                )
                state.current_dom_filtered = filter_result.payload.get("filtered_dom", dom)

                # Phase 3 — Adaptive Code Generation / Repair
                state.advance_to(Phase.GENERATION)
                if state.attempts == 0:
                    gen = self.selenium_generator.run(
                        ctx={
                            "task": task,
                            "filtered_dom": state.current_dom_filtered,
                        },
                        images=(shot,),
                    )
                    state.current_code = gen.payload.get("code", "")
                else:
                    rep = self.error_handler.run(
                        ctx={
                            "task": task,
                            "previous_code": state.current_code,
                            "error_log": state.last_error,
                            "filtered_dom": state.current_dom_filtered,
                        },
                        images=(shot,),
                    )
                    state.current_code = rep.payload.get("code", state.current_code)

                # Execute
                exec_result = self.selenium_executor.execute(state.current_code)
                if exec_result["status"] == "PASS":
                    report.suite.append(state.current_code)
                    success = True
                    metric["status"] = "PASS"
                else:
                    state.last_error = exec_result
                    state.attempts += 1
                    metric["attempts"] = state.attempts

            if not success:
                metric["status"] = "FAIL"
                report.per_task_metrics.append(metric)
                report.total_retries += state.attempts
                raise AbortError(
                    f"Unrecoverable failure on task {state.current_task_index}: {state.current_task}"
                )

            report.total_retries += state.attempts
            report.per_task_metrics.append(metric)
        state.advance_to(Phase.DONE)
