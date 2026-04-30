"""Regenerate paper Tables 1–5 from the contents of ``traces/``.

Usage:
    python -m evaluation.plot_tables --rq 1     # → evaluation/out/table1.tex
    python -m evaluation.plot_tables --rq 2     # → evaluation/out/table2.tex
    python -m evaluation.plot_tables --rq 3
    python -m evaluation.plot_tables --rq ablation
    python -m evaluation.plot_tables --rq cost
    python -m evaluation.plot_tables --rq all   # all of the above
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

from .stats import wilson_interval, mean_std


_OUT = Path(__file__).resolve().parent / "out"
_TRACES = Path(__file__).resolve().parent.parent / "traces"


# ----- Table 1 — RQ1 generation effectiveness ---------------------------

_RQ1_ROWS = [
    ("Industrial (Angular)",       "Sc.1 (Exploratory)",      "industrial_sc1_exploratory"),
    ("Industrial (Angular)",       "Sc.2 (Constrained)",      "industrial_sc2_constrained"),
    ("Industrial (Angular)",       "Sc.3 (Dynamic)",          "industrial_sc3_dynamic"),
    ("Industrial (Angular)",       "Sc.4 (Edge Case)",        "industrial_sc4_edge"),
    ("CodeBites (React)",          "Form CRUD",               "codebites_form_crud"),
    ("RoCooky (Vue.js)",           "Navigation",              "rocooky_navigation"),
    ("PRATICA-DAI (Node.js)",      "e-Commerce",              "pratica_dai_ecommerce"),
    ("Taboo (WebSocket)",          "Game Flow",               "taboo_game_flow"),
    ("RealWorld$^\\dagger$ (React)", "Registration + CRUD",    "realworld_reg_crud"),
]


def _load_runs(rq: str, scenario: str) -> list[dict]:
    paths = list((_TRACES / rq).glob(f"{scenario}_run*.json"))
    paths += list((_TRACES / "industrial_redacted" / rq).glob(f"{scenario}_run*.json"))
    return [json.loads(p.read_text()) for p in paths]


def render_table1() -> str:
    rows: list[str] = []
    total_pass = total_runs = 0
    total_tokens = 0
    total_time = 0.0
    for app, scen, key in _RQ1_ROWS:
        runs = _load_runs("rq1", key)
        if not runs:
            continue
        n = len(runs)
        passed = sum(1 for r in runs if r["status"] == "PASS")
        tasks = [r["task_count"] for r in runs]
        retries = [r["total_retries"] / max(1, r["task_count"]) for r in runs]
        tokens = [r["total_tokens"] for r in runs]
        time_min = [r["elapsed_seconds"] / 60.0 for r in runs]
        tm, ts = mean_std(tasks)
        sm = passed / n
        rm, _ = mean_std(retries)
        tk, _ = mean_std(tokens)
        tn_m, tn_s = mean_std(time_min)
        rows.append(
            f"{app} & {scen} & ${tm:.1f} \\pm {ts:.1f}$ & {sm*100:.0f}\\% & {rm:.1f} & {tk:,.0f} & ${tn_m:.1f} \\pm {tn_s:.1f}$ \\\\"
        )
        total_pass += passed
        total_runs += n
        total_tokens += tk
        total_time += tn_m
    aggregate_sr = total_pass / total_runs if total_runs else 0.0
    avg_tokens = total_tokens / max(1, len(_RQ1_ROWS))
    avg_time = total_time / max(1, len(_RQ1_ROWS))
    lo, hi = wilson_interval(total_pass, total_runs)
    return (
        "\\begin{tabular}{llccccc}\n\\toprule\n"
        "\\textbf{Application} & \\textbf{Scenario} & \\textbf{Tasks ($\\mu \\pm \\sigma$)} & "
        "\\textbf{SR} & \\textbf{Avg Retries} & \\textbf{Avg Tokens} & \\textbf{Time (min)} \\\\\n\\midrule\n"
        + "\n".join(rows)
        + "\n\\midrule\n"
        f"\\multicolumn{{2}}{{l}}{{\\textbf{{Aggregate ({total_runs} runs)}}}} & --- & "
        f"\\textbf{{{aggregate_sr*100:.1f}\\%}} & --- & {avg_tokens:,.0f} & ${avg_time:.1f}$ \\\\\n"
        f"\\multicolumn{{7}}{{l}}{{\\textit{{95\\% Wilson CI: [{lo*100:.1f}\\%, {hi*100:.1f}\\%]}}}} \\\\\n"
        "\\bottomrule\n\\end{tabular}\n"
    )


# ----- Table 2 — RQ2 mutation analysis ---------------------------------

_RQ2_ROWS = [
    ("Industrial",            "Sc.2 (Filters)",     "industrial_sc2"),
    ("Industrial",            "Sc.3 (Booking)",     "industrial_sc3"),
    ("Industrial",            "Sc.4 (Waitlist)",    "industrial_sc4"),
    ("CodeBites",             "Create Recipe",      "codebites"),
    ("PRATICA-DAI",           "Add to Cart",        "pratica_dai"),
    ("RoCooky",               "Social Sharing",     "rocooky"),
    ("Taboo",                 "Start Game",         "taboo"),
    ("RealWorld$^\\dagger$",    "Reg. + CRUD",        "realworld"),
]


def render_table2() -> str:
    rows = []
    op_totals = defaultdict(lambda: [0, 0])  # [detected, total]
    grand_detected = grand_total = 0
    for subject, scen, key in _RQ2_ROWS:
        path = _TRACES / "rq2" / f"{key}_outcomes.json"
        if not path.exists():
            path = _TRACES / "industrial_redacted" / "rq2" / f"{key}_outcomes.json"
        if not path.exists():
            continue
        out = json.loads(path.read_text())
        cells = []
        per_op = out["per_operator"]  # {AM: [det, tot], ...}
        for op in ("AM", "ER", "SLI", "EHD"):
            det, tot = per_op.get(op, [0, 0])
            cells.append(f"{det}/{tot}")
            op_totals[op][0] += det
            op_totals[op][1] += tot
        det_total, tot_total = out["totals"]
        rows.append(
            f"{subject} & {scen} & {cells[0]} & {cells[1]} & {cells[2]} & {cells[3]} & "
            f"\\textbf{{{det_total}/{tot_total}}} \\\\"
        )
        grand_detected += det_total
        grand_total += tot_total
    rate = grand_detected / max(1, grand_total)
    return (
        "\\begin{tabular}{llccccc}\n\\toprule\n"
        "\\textbf{Subject} & \\textbf{Scenario} & \\textbf{AM} & \\textbf{ER} & "
        "\\textbf{SLI} & \\textbf{EHD} & \\textbf{Detected / Total} \\\\\n\\midrule\n"
        + "\n".join(rows)
        + "\n\\midrule\n"
        f"\\textbf{{Total}} & & "
        f"\\textbf{{{op_totals['AM'][0]}/{op_totals['AM'][1]}}} & "
        f"\\textbf{{{op_totals['ER'][0]}/{op_totals['ER'][1]}}} & "
        f"\\textbf{{{op_totals['SLI'][0]}/{op_totals['SLI'][1]}}} & "
        f"\\textbf{{{op_totals['EHD'][0]}/{op_totals['EHD'][1]}}} & "
        f"\\textbf{{{grand_detected}/{grand_total} ({rate*100:.1f}\\%)}} \\\\\n"
        "\\bottomrule\n\\end{tabular}\n"
    )


# ----- Table 3 — RQ3 comparative ----------------------------------------

def render_table3() -> str:
    summary = json.loads((_TRACES / "rq3" / "summary.json").read_text())
    rows = []
    for name in ("doc2test", "sp_llm_cot", "sa_react", "sp_llm", "record_replay"):
        s = summary[name]
        sr = "N/A (Manual)" if s["generation_sr"] is None else f"{s['generation_sr']*100:.1f}\\%"
        rob = f"{s['robustness']*100:.1f}\\%" if s["robustness"] is not None else "N/A"
        tok = f"{s['avg_tokens']:,.0f}" if s["avg_tokens"] is not None else "N/A"
        rows.append(f"{s['display_name']} & {sr} & {rob} & {tok} \\\\")
    return (
        "\\begin{tabular}{lccc}\n\\toprule\n"
        "\\textbf{Approach} & \\textbf{Generation SR} & \\textbf{Robustness (Mutated)} & \\textbf{Avg. Tokens / Scenario} \\\\\n\\midrule\n"
        + "\n".join(rows)
        + "\n\\bottomrule\n\\end{tabular}\n"
    )


# ----- Table 4 — Ablation ----------------------------------------------

def render_table4() -> str:
    rows: list[str] = []
    summary = json.loads((_TRACES / "ablation" / "summary.json").read_text())
    for entry in summary["topology"]:
        rows.append(f"\\quad {entry['label']} & {entry['sr']*100:.0f}\\% & {entry['avg_tokens']:,.0f} & {entry['note']} \\\\")
    rows.append("\\midrule")
    rows.append("\\multicolumn{4}{l}{\\textit{(B) Leave-one-out}} \\\\")
    for entry in summary["leave_one_out"]:
        rows.append(f"\\quad {entry['label']} & {entry['sr']*100:.0f}\\% & {entry['avg_tokens']:,.0f} & {entry['note']} \\\\")
    return (
        "\\begin{tabular}{lccc}\n\\toprule\n"
        "\\textbf{Configuration} & \\textbf{SR} & \\textbf{Avg Tokens} & \\textbf{Note} \\\\\n\\midrule\n"
        "\\multicolumn{4}{l}{\\textit{(A) Topology ablation}} \\\\\n"
        + "\n".join(rows)
        + "\n\\bottomrule\n\\end{tabular}\n"
    )


# ----- Table 5 — Cost breakdown ----------------------------------------

def render_table5() -> str:
    csv_path = _TRACES / "cost_breakdown.csv"
    rows = list(csv.DictReader(csv_path.open()))
    out_rows = []
    total_in = total_out = 0
    total_cost = 0.0
    for r in rows:
        in_tok = int(r["input_tokens"])
        out_tok = int(r["output_tokens"])
        cost = float(r["cost_usd"])
        out_rows.append(
            f"{r['phase']} & {r['model']} & {in_tok:,} & {out_tok:,} & \\${cost:.3f} \\\\"
        )
        total_in += in_tok; total_out += out_tok; total_cost += cost
    return (
        "\\begin{tabular}{lcrrc}\n\\toprule\n"
        "\\textbf{Phase} & \\textbf{Model} & \\textbf{Input tok.} & \\textbf{Output tok.} & \\textbf{Cost (USD)} \\\\\n\\midrule\n"
        + "\n".join(out_rows)
        + "\n\\midrule\n"
        f"\\textbf{{Total}} & & \\textbf{{{total_in:,}}} & \\textbf{{{total_out:,}}} & \\textbf{{\\${total_cost:.3f}}} \\\\\n"
        "\\bottomrule\n\\end{tabular}\n"
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rq", choices=["1", "2", "3", "ablation", "cost", "all"], required=True)
    args = ap.parse_args()
    _OUT.mkdir(parents=True, exist_ok=True)
    targets = ["1", "2", "3", "ablation", "cost"] if args.rq == "all" else [args.rq]
    renderers = {"1": render_table1, "2": render_table2, "3": render_table3, "ablation": render_table4, "cost": render_table5}
    files = {"1": "table1.tex", "2": "table2.tex", "3": "table3.tex", "ablation": "table4.tex", "cost": "table5.tex"}
    for t in targets:
        out = _OUT / files[t]
        out.write_text(renderers[t]())
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
