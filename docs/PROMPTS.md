# Prompt catalogue (audit-ready)

> Every Doc2Test agent is a thin Python class that delegates to an LLM
> through the templates listed below. Each template is materialised under
> `doc2test/prompts/` so reviewers can audit the full text without
> running the framework.

## Phase 1 — Automated Requirements Analysis (8 agents)

| # | Agent | System prompt | User prompt | Output schema |
|---|---|---|---|---|
| 1 | Extractor | [`prompts/phase1/extractor.system.j2`](../doc2test/prompts/phase1/extractor.system.j2) | [`extractor.user.j2`](../doc2test/prompts/phase1/extractor.user.j2) | [`phase1_extractor.json`](../doc2test/schemas/phase1_extractor.json) |
| 2 | Structuring | [`structuring.system.j2`](../doc2test/prompts/phase1/structuring.system.j2) | [`structuring.user.j2`](../doc2test/prompts/phase1/structuring.user.j2) | [`phase1_structuring.json`](../doc2test/schemas/phase1_structuring.json) |
| 3 | Action Concretizer | [`action_concretizer.system.j2`](../doc2test/prompts/phase1/action_concretizer.system.j2) | [`action_concretizer.user.j2`](../doc2test/prompts/phase1/action_concretizer.user.j2) | [`phase1_action_concretizer.json`](../doc2test/schemas/phase1_action_concretizer.json) |
| 4 | Atomicity Enforcer | [`atomicity_enforcer.system.j2`](../doc2test/prompts/phase1/atomicity_enforcer.system.j2) | [`atomicity_enforcer.user.j2`](../doc2test/prompts/phase1/atomicity_enforcer.user.j2) | [`phase1_atomicity_enforcer.json`](../doc2test/schemas/phase1_atomicity_enforcer.json) |
| 5 | Logic Simplifier | [`logic_simplifier.system.j2`](../doc2test/prompts/phase1/logic_simplifier.system.j2) | [`logic_simplifier.user.j2`](../doc2test/prompts/phase1/logic_simplifier.user.j2) | [`phase1_logic_simplifier.json`](../doc2test/schemas/phase1_logic_simplifier.json) |
| 6 | Context Enricher | [`context_enricher.system.j2`](../doc2test/prompts/phase1/context_enricher.system.j2) | [`context_enricher.user.j2`](../doc2test/prompts/phase1/context_enricher.user.j2) | [`phase1_context_enricher.json`](../doc2test/schemas/phase1_context_enricher.json) |
| 7 | Syntax Adapter | [`syntax_adapter.system.j2`](../doc2test/prompts/phase1/syntax_adapter.system.j2) | [`syntax_adapter.user.j2`](../doc2test/prompts/phase1/syntax_adapter.user.j2) | [`phase1_syntax_adapter.json`](../doc2test/schemas/phase1_syntax_adapter.json) |
| 8 | Reorderer | [`reorderer.system.j2`](../doc2test/prompts/phase1/reorderer.system.j2) | [`reorderer.user.j2`](../doc2test/prompts/phase1/reorderer.user.j2) | [`phase1_reorderer.json`](../doc2test/schemas/phase1_reorderer.json) |

## Phase 2 — Dynamic Context Perception (1 LLM agent)

| Agent | System prompt | User prompt | Output schema |
|---|---|---|---|
| DOM Filter | [`prompts/phase2/dom_filter.system.j2`](../doc2test/prompts/phase2/dom_filter.system.j2) | [`dom_filter.user.j2`](../doc2test/prompts/phase2/dom_filter.user.j2) | [`phase2_dom_filter.json`](../doc2test/schemas/phase2_dom_filter.json) |

The other three Phase-2 components (DOM Reader, Screenshot Acquirer,
Dynamic Element Detector) are deterministic Selenium-side modules and
have no prompt.

## Phase 3 — Adaptive Code Generation & Correction (2 LLM agents)

| Agent | System prompt | User prompt | Output schema |
|---|---|---|---|
| Selenium Generator | [`prompts/phase3/selenium_generator.system.j2`](../doc2test/prompts/phase3/selenium_generator.system.j2) | [`selenium_generator.user.j2`](../doc2test/prompts/phase3/selenium_generator.user.j2) | [`phase3_selenium_generator.json`](../doc2test/schemas/phase3_selenium_generator.json) |
| Error Handler | [`prompts/phase3/error_handler.system.j2`](../doc2test/prompts/phase3/error_handler.system.j2) | [`error_handler.user.j2`](../doc2test/prompts/phase3/error_handler.user.j2) | [`phase3_error_handler.json`](../doc2test/schemas/phase3_error_handler.json) |

The Selenium Executor is the deterministic Python sandbox at
`doc2test/phase3/selenium_executor.py`.

## Baselines (RQ3, paper §4.5)

| Baseline | Prompts |
|---|---|
| SP-LLM | [`prompts/baselines/sp_llm.system.j2`](../doc2test/prompts/baselines/sp_llm.system.j2) + `sp_llm.user.j2` |
| SP-LLM+CoT | [`prompts/baselines/sp_llm_cot.system.j2`](../doc2test/prompts/baselines/sp_llm_cot.system.j2) + `sp_llm_cot.user.j2` |
| SA-ReAct | [`prompts/baselines/sa_react.system.j2`](../doc2test/prompts/baselines/sa_react.system.j2) + `sa_react.user.j2` |
| Record & Replay | manual recording, no LLM (see [`baselines/record_replay/README.md`](../baselines/record_replay/README.md)) |

## Empirical tuning history

The 8-agent Phase-1 chain emerged from iterative refinement on real
client UAT documents (paper §3.3). The topology ablation in Tab. 4
positions it between under-decomposition (3 agents, 65% SR) and over-
decomposition (12 agents, 85% SR). We did **not** exhaustively explore
the combinatorial space of agent configurations; the granularity is a
local optimum on the documents we inspected.
