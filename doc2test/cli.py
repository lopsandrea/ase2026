"""Doc2Test CLI entrypoint.

Examples
--------
    doc2test run --uat uats/codebites_form_crud.pdf --url http://localhost:3001
    doc2test batch --uat-dir uats/ --url http://localhost:3001 --junit target/junit
    doc2test inspect --uat uats/codebites_form_crud.pdf   # dry run, Phase 1 only
"""
from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import asdict
from pathlib import Path

import click

from .coordinator import Coordinator
from .llm_layer import LLMInteractionLayer
from .phase1 import CHAIN as PHASE1_CHAIN
from .phase2 import DomFilterAgent, DomReader, DynamicElementDetector, ScreenshotAcquirer
from .phase3 import ErrorHandler, SeleniumExecutor, SeleniumGenerator

log = logging.getLogger("doc2test.cli")


def _build_driver(grid_url: str | None, target_url: str):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1600,1200")

    if grid_url:
        driver = webdriver.Remote(command_executor=grid_url, options=opts)
    else:
        driver = webdriver.Chrome(options=opts)

    driver.get(target_url)
    return driver


def _build_coordinator(driver, layer: LLMInteractionLayer, max_retries: int) -> Coordinator:
    return Coordinator(
        layer=layer,
        phase1_chain=[Cls(layer) for Cls in PHASE1_CHAIN],
        dom_reader=DomReader(driver),
        screenshot_acquirer=ScreenshotAcquirer(driver),
        dynamic_detector=DynamicElementDetector(driver),
        dom_filter_agent=DomFilterAgent(layer),
        selenium_generator=SeleniumGenerator(layer),
        selenium_executor=SeleniumExecutor(driver),
        error_handler=ErrorHandler(layer),
        max_retries=max_retries,
    )


@click.group()
@click.option("-v", "--verbose", count=True)
def main(verbose: int) -> None:
    level = logging.WARNING - 10 * verbose
    logging.basicConfig(level=max(level, logging.DEBUG), format="%(asctime)s %(name)s %(levelname)s %(message)s")


@main.command("run")
@click.option("--uat", required=True, type=click.Path(exists=True))
@click.option("--url", required=True)
@click.option("--grid", default=lambda: os.environ.get("SELENIUM_GRID_URL"))
@click.option("--max-retries", default=lambda: int(os.environ.get("DOC2TEST_MAX_RETRIES", "3")))
@click.option("--out-suite", default="target/suites")
@click.option("--out-report", default="target/reports")
def run(uat: str, url: str, grid: str | None, max_retries: int, out_suite: str, out_report: str) -> None:
    """Generate and execute a Selenium suite for a single UAT document."""
    Path(out_suite).mkdir(parents=True, exist_ok=True)
    Path(out_report).mkdir(parents=True, exist_ok=True)

    driver = _build_driver(grid, url)
    layer = LLMInteractionLayer()
    coord = _build_coordinator(driver, layer, max_retries)
    try:
        report = coord.run(document=uat, target_url=url)
    finally:
        driver.quit()

    stem = Path(uat).stem
    Path(out_suite, f"{stem}.py").write_text("\n\n".join(report.suite))
    Path(out_report, f"{stem}.json").write_text(json.dumps(asdict(report), indent=2, ensure_ascii=False))

    click.echo(f"status={report.status} tasks={len(report.tasks)} retries={report.total_retries} "
               f"in_tok={report.total_input_tokens} out_tok={report.total_output_tokens} "
               f"elapsed={report.elapsed_seconds:.1f}s")
    sys.exit(0 if report.status == "PASS" else 1)


@main.command("batch")
@click.option("--uat-dir", required=True, type=click.Path(exists=True))
@click.option("--url", required=True)
@click.option("--grid", default=lambda: os.environ.get("SELENIUM_GRID_URL"))
@click.option("--junit", default="target/junit")
@click.option("--max-retries", default=3)
def batch(uat_dir: str, url: str, grid: str | None, junit: str, max_retries: int) -> None:
    """Run every UAT under a directory and emit a JUnit XML aggregate."""
    from junitparser import JUnitXml, TestSuite, TestCase, Failure

    Path(junit).mkdir(parents=True, exist_ok=True)
    aggregate = JUnitXml()

    for path in sorted(Path(uat_dir).glob("*.pdf")):
        driver = _build_driver(grid, url)
        layer = LLMInteractionLayer()
        coord = _build_coordinator(driver, layer, max_retries)
        try:
            report = coord.run(document=str(path), target_url=url)
        finally:
            driver.quit()

        suite = TestSuite(path.stem)
        for metric in report.per_task_metrics:
            case = TestCase(name=metric.get("task_id", "task"), classname=path.stem)
            if metric.get("status") != "PASS":
                case.result = [Failure(message=f"failed after {metric.get('attempts', 0)} attempts")]
            suite.add_testcase(case)
        aggregate.add_testsuite(suite)

    aggregate.write(str(Path(junit) / "aggregate.xml"))


@main.command("inspect")
@click.option("--uat", required=True, type=click.Path(exists=True))
def inspect(uat: str) -> None:
    """Run only Phase 1 against a UAT — useful for prompt-tuning diagnostics."""
    layer = LLMInteractionLayer()
    ctx: dict = {"document_path": uat}
    for Cls in PHASE1_CHAIN:
        agent = Cls(layer)
        result = agent.run(ctx=ctx)
        ctx[agent.name] = result.payload
        ctx["previous"] = result.payload
        click.echo(f"--- {agent.name} (cached={result.cached}, in={result.input_tokens}, out={result.output_tokens}) ---")
        click.echo(json.dumps(result.payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
