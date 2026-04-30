# Doc2Test

> An Industrial Multi-Agent Framework for Document-Driven End-to-End Selenium Test Generation.
> Replication package for the ASE'26 Industry Showcase paper of the same title.

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](pyproject.toml)
[![Zenodo DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.XXXXXXX-blue.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)

Doc2Test translates unstructured UAT documents (PDF / DOCX / PPTX) into executable Selenium suites through a 3-phase Multi-Agent System: 11 LLM-driven agents + 4 deterministic infrastructure modules, coordinated by a stateful orchestrator with a bounded self-healing loop.

## What's in this repository

| Directory | Purpose |
|---|---|
| `doc2test/` | Core framework: Coordinator, LLM Interaction Layer, Phase 1/2/3 agents, dashboard, CLI |
| `doc2test/prompts/` | All **11 agent prompt templates** (Jinja2), exposed integrally for audit (paper §6) |
| `doc2test/schemas/` | All 11 input/output JSON schemas enforced by the LLM Layer |
| `apps/` | 4 OSS Wideverse applications (CodeBites, PRATICA-DAI, RoCooky, Taboo) + RealWorld submodule |
| `uats/` | 9 evaluation UAT documents (4 industrial *redacted* + 5 cross-framework) |
| `baselines/` | 4 baselines for RQ3: SP-LLM, SP-LLM+CoT, SA-ReAct, Record & Replay |
| `mutation_tool/` | AST-based mutation generator (4 operators: ER, AM, SLI, EHD) |
| `evaluation/` | Reproduction harness for Tables 1–5 (RQ1, RQ2, RQ3, Ablation, Cost) |
| `traces/` | Raw execution logs (90 RQ1 runs, 180 mutation outcomes, baselines, ablation) |
| `deployment/` | Jenkinsfile + Docker + monitoring hooks (paper §5) |
| `docs/` | ARCHITECTURE / REPLICATION / PROMPTS / COSTS / LIMITATIONS |

## Quickstart

```bash
git clone https://github.com/wideverse/doc2test.git
cd doc2test
git submodule update --init --recursive   # pulls RealWorld
cp .env.example .env                       # add OPENAI_API_KEY / GEMINI_API_KEY (optional, see "Offline replay")

docker compose up -d                       # framework + Selenium grid + 4 OSS apps
docker compose run --rm doc2test \
    run --uat uats/codebites_form_crud.pdf --url http://codebites:3000
```

The CLI emits a Python+Selenium suite under `target/suites/` plus a JUnit XML report under `target/junit/`.

## Reproducing the paper tables

The default replay mode does **not** require API keys: every LLM call hits a deterministic disk cache pre-populated at submission time.

```bash
make rq1        # reproduces Table 1 (Generation Effectiveness, 94.4% aggregate SR)
make rq2        # reproduces Table 2 (Mutation Analysis, 98.9% detection rate)
make rq3        # reproduces Table 3 (Comparative Performance vs 4 baselines)
make ablation   # reproduces Table 4 (Topology + Leave-one-out)
make cost       # reproduces Table 5 (API cost breakdown)
make tables     # all of the above
```

Each target writes a regenerated `.tex` file under `evaluation/out/` byte-identical to what is rendered in the paper.

### Offline replay vs live API

- `DOC2TEST_OFFLINE=1` (default in CI): all LLM calls served from `~/.doc2test/cache/`. Output identical to the paper.
- `DOC2TEST_OFFLINE=0` with valid API keys: live calls. Numbers may differ from the paper due to LLM model drift (results frozen 2026-04-29).

## Industrial application (NDA)

The four production scenarios on the cruise-booking platform (Sc.1–Sc.4 in Table 1, Sc.2–Sc.4 in Table 2) cannot be re-executed by reviewers due to NDA constraints (paper §4.1, footnote 1). We provide:

- **Redacted JSON traces** under `traces/industrial_redacted/` (40 runs RQ1 + 30 mutants RQ2): tasks emitted, DOM-filter outputs, generated code stubs with placeholders (`[CLIENT_URL]`, `[ITINERARY_ID]`), execution status, retries, tokens, time.
- **No source code or runnable proxy** for the production application.

The remaining 50 runs (RQ1) and 150 mutants (RQ2) on the OSS subjects are fully reproducible and represent the auditable evidence base.

## Citing

```bibtex
@inproceedings{lops2026doc2test,
  title     = {Doc2Test: An Industrial Multi-Agent Framework for Document-Driven End-to-End Selenium Test Generation},
  author    = {Lops, Andrea and Ferrara, Antonio and Narducci, Fedelucio and Ragone, Azzurra and Trizio, Michelantonio},
  booktitle = {The 41st IEEE/ACM International Conference on Automated Software Engineering -- Industry Showcase (ASE '26)},
  year      = {2026},
  doi       = {XXXXXXX.XXXXXXX}
}
```

## License

- Framework, baselines, mutation tool, evaluation harness: **Apache-2.0** (see [LICENSE](LICENSE)).
- OSS subject applications: see individual `apps/*/LICENSE` (CodeBites & RoCooky: MIT; PRATICA-DAI & Taboo: Apache-2.0; RealWorld: per upstream community license).

## Acknowledgments

This work was carried out within Wideverse's R&D programme. We thank the QA team of our industrial partner for the UAT corpus and the deployment feedback that shaped the L1–L6 lessons reported in §5.
