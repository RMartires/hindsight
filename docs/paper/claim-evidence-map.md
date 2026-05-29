# Claim–evidence map (memory-aligned)

**Rule:** Each claim below must be supportable from **existing code and artifacts** described in **`.cursor/memory.md`**.

**Last updated:** 2026-05-29.

---

## System / method claims

| ID | Claim | Evidence |
|----|--------|----------|
| M1 | Multi-agent pipeline with analysts → debate → trader → risk → final decision | `graph/setup.py`, `TradingAgentsGraph`; memory `tradingagents-graph`, `tradingagents-agents` |
| M2 | Four ablation presets change which phases/analysts run *(not evaluated in §4)* | `tradingagents/paper_ablation.py`; memory `config-and-env` |
| M3 | Stages emit structured JSON aligned to Pydantic models | `tradingagents/schemas/outputs.py`, `invoke_fallback`; memory `tradingagents-schemas` |
| M4 | Vendor calls respect simulation end date (point-in-time) | `simulation_context.py`, `interface.route_to_vendor`; memory `tradingagents-dataflows` |
| M5 | Optional ticker anonymization in prompts/tool I/O | `tradingagents/anonymization/`; memory `tradingagents-anonymization` |
| M6 | Backtest applies signals with configurable cost model and metrics | `tradingagents/backtest/`; memory `tradingagents-backtest` |
| M7 | Analyst roles are tool-bound to concrete tasks (indicators, statements, news) | `tradingagents/agents/analysts/*.py`, `indicator_library.py` |

---

## Empirical claims

| ID | Claim | Evidence |
|----|--------|----------|
| E1 | The **full** pipeline (`PAPER_ABLATION=full`) on **two large-cap NSE listings** yields **observed** regime-dependent agent vs buy-and-hold outcomes under **per-ticker exogenous bear/bull windows** (N=1 trajectory per window) | Four frozen CSVs + `scripts/backtest_regime_analysis.ipynb` |

**Not claimed:** multi-seed variance; index-universe generalization; SOTA Sharpe.

---

## Regime definition (Frozen E1)

**Market regimes** are assigned **exogenously** per ticker from **buy-and-hold return on that ticker’s adjusted close** over each evaluation window (first → last processed trading day). Labels are independent of agent signals and of internal **Bull/Bear Researcher** debate roles.

| Label | Rule (per ticker, per window) |
|-------|-------------------------------|
| **Bear** | Underlying B&H return **≤ −10%** |
| **Bull** | Underlying B&H return **≥ +10%** |

**Calendar windows** are pre-specified in `regime-timeranges` **before** agent backtests. Windows **differ by ticker**. Each run uses **fresh $100,000** paper cash.

---

### Frozen E1 — four windows (two tickers × two regimes)

| Ticker | Regime | Calendar intent | Processed window | Days | Artifact CSV | Log |
|--------|--------|-----------------|------------------|------|--------------|-----|
| RELIANCE.NS | Bear | Aug 2024 – Jan 2025 | 2024-08-01 .. 2025-01-03 | 111 | `results/dates-REL-aug-2024-jan-2025-bear-dates.csv` | `eval_results/dates-REL-aug-2024-jan-2025-bear-dates.log` |
| RELIANCE.NS | Bull | Jan 2025 – Jun 2025 | 2025-01-01 .. 2025-06-03 | 108 | `results/dates-REL-jan-2025-june-2025-bull-dates.csv` | `eval_results/dates-REL-jan-2025-june-2025-bull-dates.log` |
| TCS.NS | Bear | Dec 2024 – Apr 2025 | 2024-12-02 .. 2025-04-03 | 88 | `results/dates-TCS-dec-2024-april-2025-bear-dates.csv` | `eval_results/dates-TCS-dec-2024-april-2025-bear-dates.log` |
| TCS.NS | Bull | Jun 2024 – Sep 2024 | 2024-06-03 .. 2024-09-03 | 67 | `results/dates-TCS-june-2024-sept-2024-bull-dates.csv` | `eval_results/dates-TCS-june-2024-sept-2024-bull-dates.log` |

**Shared protocol:** `PAPER_ABLATION=full`; `initial_cash=$100,000`; `cost_model=zerodha_delivery`, `slippage_bps=0`; anonymization enabled; LLM `qwen/qwen3.5-flash-02-23`; driver `scripts/backtest_mvp.py --dates-csv <artifact>`.

### Frozen metrics — Table 1 (primary)

| Ticker | Regime | B&H return | Agent (net) | Gross | Fee drag | α vs B&H | B&H MDD | Agent MDD | Fees ($) | B/H/S |
|--------|--------|------------|-------------|-------|----------|----------|---------|-----------|----------|-------|
| RELIANCE | Bear | −17.43% | −7.54% | −6.53% | 1.01 pp | +9.89 pp | 21.0% | 5.11% | 1,010.32 | 7 / 28 / 76 |
| RELIANCE | Bull | +15.09% | +5.56% | +6.19% | 0.64 pp | −9.53 pp | 11.0% | 2.80% | 635.44 | 9 / 25 / 74 |
| TCS | Bear | −20.42% | −4.83% | −2.92% | 1.91 pp | +15.59 pp | 23.9% | 6.78% | 1,909.83 | 12 / 24 / 52 |
| TCS | Bull | +21.86% | +19.61% | +21.80% | 2.20 pp | −2.25 pp | 5.5% | 1.65% | 2,197.78 | 13 / 14 / 40 |

**Source:** daily `equity` and `close` in frozen CSVs; gross = net + fees/$100k.

### Frozen metrics — Table 2 (secondary, post-hoc)

**Excess Sharpe:** daily agent/B&H equity; $R_f = 6.5\%$ p.a. → daily $r_f/252$; annualized $\sqrt{252}$.

| Ticker | Regime | Excess Sharpe (agent) | Excess Sharpe (B&H) | Sortino | Calmar |
|--------|--------|----------------------|---------------------|---------|--------|
| RELIANCE | Bear | −4.27 | −2.51 | −3.10 | −0.96 |
| RELIANCE | Bull | +0.74 | +1.25 | +3.67 | +1.94 |
| TCS | Bear | −2.69 | −3.13 | −2.25 | −0.71 |
| TCS | Bull | +3.86 | +3.27 | +24.22 | +11.88 |

**Cross-ticker summary:** Bear windows: positive alpha vs B&H, lower MDD. Bull windows: heterogeneous alpha; REL bull under-participation not explained by fee drag alone.

**Analysis / figures:** `scripts/backtest_regime_analysis.ipynb`, `scripts/generate_paper_figures.py`.

**Retired:** `results/_retired/`. **Planned but not in §4:** Infosys windows in `regime-timeranges`.

---

## Forbidden in camera-ready unless you have proof

- Regime labels from agent outlook columns.
- “Same calendar across tickers.”
- SOTA, regime-prediction, or multi-seed generalization claims.
- “Four independent runs” meaning four **seeds** (use **four regime windows**).

---

## Changelog

| Date | Note |
|------|------|
| 2026-05-28 | Initial regime freeze (RELIANCE only). |
| 2026-05-29 | Multi-ticker Frozen E1: REL bull + TCS bear/bull. |
| 2026-05-29 | Reviewer revision: reframe case study; excess Sharpe; extended tables; N=1 scope. |
