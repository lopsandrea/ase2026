# Architecture

> Reading order: [paper §3](../README.md#paper) → this file → the prompts
> in [PROMPTS.md](PROMPTS.md). The figures `phase_1.png`, `phase_2.png`,
> `phase_3.png` from the paper render the same data flow described here.

## High-level

```
┌─────────────┐  ┌──────────────────────────────────────────────────────────┐
│  UAT (PDF / │  │                       Doc2Test                            │
│  DOCX/PPTX) ├──▶                                                            │
└─────────────┘  │  ┌─────────────────────────────────────────────────────┐  │
                 │  │ Phase 1 — Automated Requirements Analysis (8 LLM)   │  │
                 │  │ Extractor → Structuring → Action Concretizer        │  │
                 │  │  → Atomicity Enforcer → Logic Simplifier            │  │
                 │  │  → Context Enricher → Syntax Adapter → Reorderer    │  │
                 │  └─────────────────────────────────────────────────────┘  │
                 │                          │ task list (JSON)               │
                 │  ┌──────────────▼──────────────────────────────────────┐  │
                 │  │ Coordinator (per-task loop, max retries M=3)        │  │
                 │  └──────────────┬──────────────────────────────────────┘  │
                 │  ┌──────────────▼──────────────────────────────────────┐  │
                 │  │ Phase 2 — Dynamic Context Perception                │  │
                 │  │ DOM Reader · Screenshot Acquirer · Dynamic Detector │  │
                 │  │ DOM Filter Agent (LLM, multimodal grounding)        │  │
                 │  └──────────────┬──────────────────────────────────────┘  │
                 │  ┌──────────────▼──────────────────────────────────────┐  │
                 │  │ Phase 3 — Adaptive Code Generation & Correction     │  │
                 │  │ Selenium Generator (LLM, multimodal)                │  │
                 │  │ Selenium Executor (deterministic)                   │  │
                 │  │ Error Handler (LLM, ReAct repair)                   │  │
                 │  └─────────────────────────────────────────────────────┘  │
                 │                          │                                │
                 │              executable Selenium suite                    │
                 └──────────────────────────────────────────────────────────┘
```

## Component → file map

| Paper concept | Concrete file |
|---|---|
| Algorithm 1 (orchestration) | `doc2test/coordinator/coordinator.py` |
| State machine (Phase enum) | `doc2test/coordinator/state_machine.py` |
| Exponential-backoff retry | `doc2test/coordinator/retry.py` |
| LLM Interaction Layer (§3.1) | `doc2test/llm_layer/` |
| 8 Phase-1 agents (Tab. 1) | `doc2test/phase1/*.py` + `doc2test/prompts/phase1/*.j2` |
| 4 Phase-2 components (Tab. 2) | `doc2test/phase2/*.py` |
| 3 Phase-3 components (Tab. 3) | `doc2test/phase3/*.py` |
| 11 prompt templates | `doc2test/prompts/` |
| 11 JSON schemas | `doc2test/schemas/` |
| Real-time dashboard | `doc2test/ui/server.py` |
| CLI | `doc2test/cli.py` |

## Data contracts

Inter-phase communication is **strictly JSON**, validated at every hop
against the per-agent schema. The handshake is:

1. Phase 1 emits `Reorderer` output (`schemas/phase1_reorderer.json`):
   a list of `{id, title, description, preconditions[], input_bindings[],
   expected_outcome}` task objects.
2. The Coordinator iterates over the list, calling Phase 2 then Phase 3
   per task.
3. Phase 2's DOM Filter emits `{filtered_dom, rationale,
   candidate_locators[]}` (`schemas/phase2_dom_filter.json`).
4. Phase 3's Selenium Generator emits `{code, locator_strategy,
   assertions[], explicit_waits[]}` (`schemas/phase3_selenium_generator.json`).
5. On runtime failure, Phase 3's Error Handler emits `{code | give_up,
   diagnosis, repair_strategy}` (`schemas/phase3_error_handler.json`).

If any agent's output fails its schema, the LLM Interaction Layer raises
`SchemaValidationError`. The Coordinator counts that as a retry and re-
invokes Phase 2 + 3 with a fresh DOM/screenshot.

## Provider allocation (paper Tab. 5)

| Phase | Provider | Model | Temperature | Top-p |
|---|---|---|---|---|
| 1 (8 agents) | OpenAI | `gpt-5-0326-2026` | 0.2 | 0.95 |
| 2 (DOM Filter) | Google | `gemini-2.5-pro-preview-03-25` | 0.2 | 0.95 |
| 3 (2 agents)  | OpenAI | `gpt-5-0326-2026` | 0.2 | 0.95 |

The provider-agnostic boundary is `doc2test.llm_layer.LLMInteractionLayer`,
so swapping a model is a one-line change in each agent's `model` class
attribute.
