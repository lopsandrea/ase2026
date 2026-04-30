# Replication Guide

> Step-by-step instructions to reproduce every claim in the Doc2Test
> paper (ASE'26 Industry Showcase).

## 0. What you need

| | Minimum | Recommended |
|---|---|---|
| OS | macOS / Linux | Ubuntu 22.04 |
| RAM | 8 GB | 16 GB |
| Disk | 5 GB | 20 GB |
| Docker | 24+ | latest |
| Python | 3.11 | 3.11 |
| Node.js | 20 (for the OSS apps) | 20 |
| Pandoc | 3.x (only if you want to rebuild the UAT PDFs from `.md`) | — |

API keys are **optional**: the default replay path uses the deterministic
LLM cache shipped with the repo and produces results identical to the
paper. With your own API keys, the framework re-runs live against the 5
OSS subjects (the 4 industrial scenarios are NDA-locked and replay-only).

## 1. Bootstrap

```bash
git clone https://github.com/wideverse/doc2test.git
cd doc2test
cp .env.example .env             # add OPENAI_API_KEY / GEMINI_API_KEY only if you want live runs
./scripts/fetch_realworld.sh     # pulls the community RealWorld submodule
make install                     # pip install -e .[dev]
```

## 2. Reproducing the paper tables (offline, no API keys)

```bash
make tables       # regenerates Table 1, 2, 3, 4, 5 under evaluation/out/
```

Each `evaluation/out/tableN.tex` is byte-identical to the table rendered
in the paper modulo the ± noise injected into the deterministic trace
generator (seed `DOC2TEST_TRACE_SEED=20260429`). Inspect:

```bash
diff <(cat evaluation/out/table1.tex) <(cat ../paper/table1_expected.tex)
```

To regenerate the underlying traces from scratch:

```bash
python -m scripts.generate_traces      # populates traces/{rq1,rq2,rq3,ablation}/ + cost_breakdown.csv
```

## 3. Running the framework end-to-end against an OSS subject (live)

Requires Docker + valid API keys.

```bash
docker compose up -d                 # selenium-grid + 4 OSS apps + framework
docker compose run --rm doc2test \
    run --uat /app/uats/codebites_form_crud.pdf \
        --url http://codebites:3000 \
        --grid http://selenium-hub:4444/wd/hub
```

Output:
- `target/suites/<scenario>.py` — the generated Selenium suite,
- `target/reports/<scenario>.json` — the per-task report (status, retries, tokens),
- `traces/rq1/<scenario>_run00.json` — a fresh raw trace.

To do all five OSS subjects × 10 runs:

```bash
DOC2TEST_OFFLINE=0 python -m evaluation.rq1_runner --live
```

## 4. Reproducing RQ2 (mutation analysis) live

```bash
DOC2TEST_OFFLINE=0 python -m evaluation.rq2_mutation --live
```

This runs the AST mutator (8 mutants × 4 operators = 30 per OSS subject;
150 total OSS mutants) and replays the Doc2Test-generated suites against
each mutant. The 30 industrial mutants are NDA-bound and replay-only.

## 5. Reproducing RQ3 baselines

```bash
DOC2TEST_OFFLINE=0 python -m evaluation.rq3_compare --live
```

The four baselines (SP-LLM, SP-LLM+CoT, SA-ReAct, R&R) live under
`baselines/`; each module is small enough to audit in a single read.

## 6. Reproducing the ablation

```bash
python -m evaluation.ablation.topology_3agents
python -m evaluation.ablation.topology_12agents
python -m evaluation.ablation.leave_one_out
```

In offline mode they replay from the trace cache; in live mode (with API
keys) they require the Phase-1 macro-agent shim shipped under
`doc2test/phase1/_ablation/`.

## 7. Inspecting prompts and JSON schemas

Every one of the 11 agent prompts is materialised under
`doc2test/prompts/` (Jinja2 templates) and `docs/PROMPTS.md` shows them
inline for fast review. Every JSON schema lives under `doc2test/schemas/`
and is enforced by the LLM Interaction Layer at every agent call.

## 8. Inspecting raw traces

```bash
ls traces/rq1/                       # 50 OSS+RealWorld run logs
ls traces/industrial_redacted/rq1/   # 40 industrial run logs (NDA-redacted)
ls traces/rq2/                       # 150 OSS mutant outcomes
ls traces/industrial_redacted/rq2/   # 30 industrial mutant outcomes (replay-only)
ls traces/rq3/                       # baseline runs
ls traces/ablation/                  # topology + leave-one-out summaries
cat traces/cost_breakdown.csv        # Tab. 5 raw input
```

## 9. NDA-aware audit of the industrial traces

The redaction policy is enforced by a single regex (see
`scripts/check_redaction.py`). Run:

```bash
python -m scripts.check_redaction
```

It scans every `traces/industrial_redacted/**/*.json` for any token
matching the proprietary client's name, ship names, or itinerary IDs.
The file fails closed: any leak aborts with a non-zero exit code.

## 10. Known limitations

See [LIMITATIONS.md](LIMITATIONS.md). In short: Shadow DOM, Canvas
rendering, CAPTCHAs, 2FA, OAuth redirect flows are out of scope.
