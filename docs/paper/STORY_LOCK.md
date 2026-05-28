# Story lock (memory-aligned)

**Scope:** Claims and framing must match **`.cursor/memory.md`** — no dependence on features that exist only in `ROADMAP.md` as unbuilt work.

**Last updated:** 2026-05-28.

---

## Title and pitch (working — refine with co-authors)

**Working title:** *Point-in-Time Multi-Agent LLM Trading: A Reproducible LangGraph Stack with Regime-Conditioned Evaluation and Fair Backtesting*

**One-line pitch:** We describe an open **LangGraph** trading pipeline with specialist analysts, bull/bear **debate roles**, and risk critique, **structured outputs** per stage, a **simulation date cap**, optional **ticker anonymization**, and a **paper backtest**. §4 evaluates the **full** pipeline on **RELIANCE.NS** under two **exogenous market regimes** (bear and bull windows) with agent vs buy-and-hold comparison on historical as-of dates.

---

## Naming

| Context | Name |
|--------|------|
| Product / repo / supplementary | **Hindsight 20/20** |
| Blind manuscript (if required) | Neutral: “our implementation,” “the open-source stack” |
| **Market regime** (§4) | Exogenous calendar window labeled bear/bull from underlying return |
| **Bull/Bear Researcher** (§3) | Internal debate agents — not the same as market regime |

---

## Contributions (must be traceable to memory modules)

**Manuscript:** [manuscript.md](manuscript.md). **Roadmap & progress:** [paper-roadmap.md](paper-roadmap.md).

| ID | Contribution | Grounding (memory) |
|----|----------------|---------------------|
| **S1** | **Multi-agent decision graph** with debate phases | `tradingagents-graph`, `tradingagents-agents` |
| **S2** | **Regime-conditioned evaluation**: same `full` pipeline, independent runs, exogenous bear/bull windows, agent vs B&H | `scripts/backtest_mvp.py`, `scripts/backtest_regime_analysis.ipynb`, Frozen E1 in `claim-evidence-map.md` |
| **S3** | **Structured stage outputs** (Pydantic schemas + JSON-in-state) | `tradingagents-schemas`, `tradingagents-llm-clients` |
| **S4** | **Fair-as-of data access**: simulation end date + vendor clamps; optional **anonymization** | `tradingagents-dataflows`, `tradingagents-anonymization` |
| **S5** | **Backtest harness**: paper ledger, fee models, performance metrics, CSV artifacts | `tradingagents-backtest`, `scripts` |

Optional **one line** in abstract: **Langfuse**-compatible tracing — operational, not an empirical claim.

---

## Related work — paragraph buckets

Agents-for-trading; leakage/memorization; **robustness across market conditions** (replacing ablation-depth framing); execution realism. **“We Y”** describes temporal cap, anonymization, structured outputs, fees, and regime-split evaluation.

**BibTeX starter:** [bib-seed.bib](bib-seed.bib).

---

## Figure / table ideas

| Idea | Source |
|------|--------|
| Pipeline / DAG | LangGraph setup + `memory/tradingagents-graph.md` (optional) |
| Regime equity vs B&H | `fig_regime_equity`, `fig_regime_returns` |
| Signal counts by regime | `fig_regime_signals` |
| Analyst bullish-share heatmap | `fig_regime_outlook_bullish` |
| Table 1 — returns, drawdown, Sharpe, signals | `backtest_regime_analysis.ipynb` |
| Table 2 — stage outlook / stance breakdown | same notebook |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-05-28 | Regime evaluation replaces ablation study; S2 rewritten; Frozen E1 bear/bull CSVs. |
