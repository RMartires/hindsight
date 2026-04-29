# Story lock (memory-aligned)

**Scope:** Claims and framing must match **`.cursor/memory.md`** — no dependence on features that exist only in `ROADMAP.md` as unbuilt work.

**Last updated:** 2026-04-29.

---

## Title and pitch (working — refine with co-authors)

**Working title:** *Point-in-Time Multi-Agent LLM Trading: A Reproducible LangGraph Stack with Ablations and Fair Backtesting*

**One-line pitch:** We describe an open **LangGraph** trading pipeline with specialist analysts, bull/bear and risk debates, **structured outputs** per stage, a **simulation date cap** and optional **ticker anonymization**, and a **paper backtest** with preset **ablations** (`a1`–`full`) so depth-of-pipeline comparisons stay reproducible on historical as-of dates.

---

## Naming

| Context | Name |
|--------|------|
| Product / repo / supplementary | **Hindsight 20/20** |
| Blind manuscript (if required) | Neutral: “our implementation,” “the open-source stack” |

---

## Contributions (must be traceable to memory modules)

**Manuscript (submit / PDF):** [manuscript.md](manuscript.md). **Roadmap & progress:** [paper-roadmap.md](paper-roadmap.md).

These map to code paths listed in `.cursor/memory.md`, not to future `ROADMAP.md` items.

| ID | Contribution | Grounding (memory) |
|----|----------------|---------------------|
| **S1** | **Multi-agent decision graph** with debate phases and configurable depth | `tradingagents-graph`, `tradingagents-agents` |
| **S2** | **Ablation presets** over the same engine (`PAPER_ABLATION` / `paper_ablation.py`) | `config-and-env`, `scripts` |
| **S3** | **Structured stage outputs** (Pydantic schemas + JSON-in-state) for an auditable trace | `tradingagents-schemas`, `tradingagents-llm-clients` |
| **S4** | **Fair-as-of data access**: simulation end date + vendor clamps; optional **anonymization** | `tradingagents-dataflows`, `tradingagents-anonymization` |
| **S5** | **Backtest harness**: paper ledger, fee models, performance metrics, CSV artifacts | `tradingagents-backtest`, `scripts` |

Optional **one line** in abstract: **Langfuse**-compatible tracing (`tradingagents-observability`, `backend`) for debugging and run correlation — not a scientific claim unless you analyze traces in the paper.

---

## Related work — paragraph buckets

Same four buckets as before (agents-for-trading, leakage/memorization, multi-agent cost, execution realism), but **“we Y”** should describe **what is implemented** (ablations, temporal cap, anonymization, structured outputs, fees), not metrics or modules from `ROADMAP.md` that are not shipped.

**BibTeX starter:** [bib-seed.bib](bib-seed.bib).

---

## Figure / table ideas (all derivable without new engine code)

| Idea | Source |
|------|--------|
| Pipeline / DAG | Topology from LangGraph setup + `memory/tradingagents-graph.md` |
| Ablation equity curves | Existing `results/*.csv`, `scripts/backtest_ablation_analysis.ipynb` |
| Metrics table | `equity.csv` / schedule columns / `metrics.py` formulas |
| Qualitative trace | `eval_results/.../full_states_log_*.json` |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-04-29 | Manuscript → `manuscript.md`; roadmap → `paper-roadmap.md` (under `docs/paper/`); root `PAPER_ROADMAP.md` is stub. |
| 2026-04-29 | Abstract, contributions, and PDF checklist consolidated into root `PAPER_ROADMAP.md`. |
| 2026-04-29 | Rewritten to drop CBS / predictive-validation / future-code roadmap dependencies; align with `memory.md`. |
