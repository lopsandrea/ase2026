# Cost analysis (paper §5, Table 5)

## Per-scenario breakdown

The published figure of **\$0.117 / scenario** comes from the
deployment-period token telemetry stored in
[`traces/cost_breakdown.csv`](../traces/cost_breakdown.csv) and rendered
to LaTeX by [`evaluation/plot_tables.py`](../evaluation/plot_tables.py)
(`make cost`).

| Phase | Model | Input tokens | Output tokens | Cost (USD) |
|---|---|---:|---:|---:|
| 1 (8 agents) | GPT-5 (`gpt-5-0326-2026`) | 8 200 | 3 100 | 0.057 |
| 2 (DOM Filter) | Gemini-2.5-pro (`gemini-2.5-pro-preview-03-25`) | 12 400 | 1 800 | 0.018 |
| 3 (2 agents) | GPT-5 (`gpt-5-0326-2026`) | 5 900 | 2 600 | 0.042 |
| **Total** | | **26 500** | **7 500** | **0.117** |

## Why the heterogeneous allocation

Lesson **L4** in the paper is that cost management was a real
constraint. The early monolithic GPT-5 deployment cost about
**\$126 / month** of nightly runs; routing the bulk-token Phase-2 DOM
filtering to Gemini-2.5-pro brought the same workload down to **\$42**
per month — roughly a **3× saving** with no measurable quality
regression on the same UAT corpus.

## Three-month deployment totals

Across ~90 nightly runs × 4 scenarios (industrial only, by far the most
expensive subjects):

- Total spend: **~\$42**.
- Replaced manual effort estimated by the partner's QA team:
  **€800–€1 200 / sprint** (≈ \$870–\$1 305 / sprint, two sprints / month
  ≈ €1 600–€2 400 / month). ROI ≳ 100×.

## Cost extrapolation

For a project that wants to estimate its own bill with Doc2Test:

```
expected_cost ≈ 0.117 USD × (#scenarios × #runs_per_night × #nights)
```

Real production deployments will see variance from token counts (input
DOM size grows superlinearly with the number of dynamic components in
the SPA) and from retry budget consumption.

## Where to look for the raw numbers

Run:

```bash
cat traces/cost_breakdown.csv
python -m evaluation.plot_tables --rq cost
cat evaluation/out/table5.tex
```

Both should match the values printed at the top of this file.
