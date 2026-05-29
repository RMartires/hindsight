# Manuscript (draft — export to PDF / LaTeX)

**Purpose:** Submission-facing prose only. Scope: [paper-roadmap.md](paper-roadmap.md). Claims: **`.cursor/memory.md`** and [claim-evidence-map.md](claim-evidence-map.md).

**Last updated:** 2026-05-29.

**PDF:** `pandoc docs/paper/manuscript.md -o paper-draft.pdf --pdf-engine=tectonic`. IOS: `./docs/paper/submission/build_ios_package.sh`.

---

## Working title

*Point-in-Time Multi-Agent LLM Trading: A Reproducible LangGraph Stack with Regime-Conditioned Evaluation and Fair Backtesting*

---

## Abstract

Large language models are increasingly used in financial decision pipelines, yet published agent stacks are often hard to reproduce and rarely evaluated under distinct **market conditions** on historical “as of” dates. We present **Hindsight 20/20**, an open **LangGraph** stack with structured **Pydantic** outputs, a **simulation end date** for point-in-time data, optional **ticker anonymization**, and a fee-aware **paper backtest**. We evaluate the **full** multi-agent pipeline on two large-cap NSE listings—**RELIANCE.NS** and **TCS.NS**—each in **exogenous bear and bull calendar windows** (per-ticker underlying return ≤ −10% or ≥ +10%), with **$100,000** fresh paper capital per run. In **both bear windows**, the agent loses **less** than buy-and-hold (RELIANCE: −7.5% vs −17.4%; TCS: −4.8% vs −20.4%). In **bull windows**, outcomes **diverge**: RELIANCE lags buy-and-hold (+5.6% vs +15.1%) while TCS nearly tracks it (+19.6% vs +21.9%). Final signals remain **SELL-heavy** across runs. Frozen CSV artifacts and scripts reproduce tables and figures. **Langfuse** tracing supports debugging only.

*(IOS submission: [`docs/paper/submission/`](submission/) — run `build_ios_package.sh`.)*

---

## 1. Introduction

Researchers are experimenting with large language models (LLMs) inside trading workflows. Yet evaluations rarely ask how the **same implementation** behaves when the **underlying trend** differs—and rarely report results on more than one name.

**Hindsight 20/20** extends the open-source **TradingAgents** multi-agent LangGraph framework (Xiao et al., 2024) with point-in-time data access, optional ticker anonymization, and a reproducible backtest harness; we evaluate this extended stack under exogenous bear and bull windows. **Structured outputs**, a **simulation end date**, and a **paper backtest** with configurable fees support point-in-time research.

**Empirical focus.** We run the **full** pipeline (`PAPER_ABLATION=full`) on **RELIANCE.NS** and **TCS.NS**. For each ticker we pre-specify one **bear** and one **bull** calendar window whose underlying buy-and-hold return meets exogenous thresholds (§4.1). Each of **four runs** starts from **$100,000** paper cash; we compare agent return to **buy-and-hold** on the same window.

**Structure.** §2 related work; §3 system; §4 experiments; §5 conclusion; **Contributions** at the end.

---

## 2. Related Work

*Starter keys: [bib-seed.bib](bib-seed.bib).*

**LLM agents for trading.** Multi-agent frameworks orchestrate specialist roles (Xiao et al., 2024; Yu et al., 2023; Yang et al., 2023). We emphasize **reproducible systems engineering**—one codepath, schema-constrained outputs, temporal controls, scriptable backtests tied to **CSV artifacts**.

**Point-in-time data and leakage.** Simulation end dates, vendor routing, and optional anonymization bound information access.

**Robustness across market conditions.** We document **regime-split** backtests on the **same** stack across **two tickers** with frozen protocols—not regime *prediction*, but *evaluation* under exogenous labels. Windows are **per ticker** because drawdowns and rallies are not synchronous.

**Execution realism.** Paper ledger with stated fees (`zerodha_delivery`); no microstructure claim.

**Positioning.** Open narrative: LangGraph orchestration, structured outputs, temporal/anonymization controls, **multi-ticker regime-conditioned** evaluation.

---

## 3. Method / System

Pointers: **`.cursor/memory.md`**.

### 3.1 Architecture

**`TradingAgentsGraph`**: analysts, **Bull/Bear Researcher** debate (*internal roles*, not §4 market regimes), trader, risk. Core analyst → debate → trader → risk routing follows **TradingAgents** (Xiao et al., 2024); our modifications focus on temporal data policy, schema-constrained outputs, and the backtest/evaluation pipeline described below. Same graph for **`run_backtest_mvp`**.

### 3.2 Tools and structured outputs

Analyst tools fetch market, news, sentiment, and fundamentals data; stage outputs conform to **Pydantic** schemas (`tradingagents/schemas/outputs.py`, **M3**).

### 3.3 Point-in-time data policy

A **simulation end date** clamps vendor queries so agents cannot access data after the as-of trade date (**M4**).

### 3.4 Ticker anonymization

Large language models trained on public text often encode firm-specific narratives—brand reputation, sector themes, and historical events—tied to ticker symbols and company names. In a point-in-time backtest, that **pretraining leakage** can bias decisions: the same vendor data may elicit different agent behavior on `RELIANCE.NS` versus an unseen alias.

Hindsight 20/20 optionally **anonymizes the issuer** for all LLM-facing prompts and tool outputs (**M5**):

1. **Deterministic ticker aliases** — `TickerMapper.for_real_ticker()` maps each real symbol to a stable synthetic id (`STOCK_####`, SHA-256–derived).
2. **Round-trip vendor access** — tool wrappers call `resolve_ticker_for_vendor()` to de-anonymize before API calls, then `scrub_ticker_text()` on responses.
3. **News scrubbing** — `scrub_news_text()` replaces multi-word proper nouns with `PROPER_NOUN` placeholders (heuristic, news-only).

Frozen E1 uses **`enable_anonymization=True`** (default in `backtest_mvp.py`). We do **not** ablate anonymization in §4; reporting with it **on** reduces name-based bias when comparing regimes and tickers.

### 3.5 Backtest metrics

The paper ledger (`tradingagents/backtest/`) records daily agent equity after fees. **`compute_performance_stats`** reports:

| Metric | Definition |
|--------|------------|
| **Total return** | \((V_T - V_0) / V_0\) on agent equity |
| **Max drawdown (MDD)** | Peak-to-trough decline on the agent equity curve; **B&H MDD** computed on buy-and-hold equity from the same adjusted closes |
| **Sharpe ratio** | Mean daily simple return / stdev, × \(\sqrt{252}\)[^sharpe252]; **no risk-free rate subtracted** in Frozen E1 |

[^sharpe252]: Annualization assumes 252 trading days per year (US equity convention). NSE calendars are typically ≈240–250 trading days; we retain 252 for comparability with standard reported Sharpe ratios.

Short windows (67–111 trading days) yield noisy Sharpe estimates, especially for discrete-signal agents. Excess Sharpe and Sortino/Calmar are implemented but not emphasized in §4.

### 3.6 Pipeline configuration

§4 uses **`PAPER_ABLATION=full`**. Presets **`a1`–`a3`** exist for internal use only (**M2**).

### 3.7 Paper backtest

**`scripts/backtest_mvp.py --dates-csv`** writes schedule CSVs (signals, equity, outlook, and analysis columns including MDD and Sharpe).

### 3.8 Observability

Langfuse optional; not empirical evidence.

---

## 4. Experiments

### 4.1 Goals, scope, and regime definition

We evaluate the **full** pipeline on **two tickers** under **exogenous market regimes**.

| Regime label | Rule (underlying B&H on processed window, per ticker) |
|--------------|--------------------------------------------------------|
| **Bear** | Total return **≤ −10%** |
| **Bull** | Total return **≥ +10%** |

**Calendar windows** are listed in **`regime-timeranges`** before agent runs. They **differ by ticker** (e.g. TCS bull is Jun–Sep 2024; RELIANCE bull is Jan–Jun 2025). Each run is **independent** with **$100,000** initial cash. We do not claim regime forecasting, optimality, or a shared macro calendar.

**Frozen artifacts:** [claim-evidence-map.md](claim-evidence-map.md) (**Frozen E1**).

### 4.2 Protocol

| Ticker | Regime | Processed window | Schedule CSV |
|--------|--------|------------------|--------------|
| RELIANCE.NS | Bear | 2024-08-01 .. 2025-01-03 | `results/dates-REL-aug-2024-jan-2025-bear-dates.csv` |
| RELIANCE.NS | Bull | 2025-01-01 .. 2025-06-03 | `results/dates-REL-jan-2025-june-2025-bull-dates.csv` |
| TCS.NS | Bear | 2024-12-02 .. 2025-04-03 | `results/dates-TCS-dec-2024-april-2025-bear-dates.csv` |
| TCS.NS | Bull | 2024-06-03 .. 2024-09-03 | `results/dates-TCS-june-2024-sept-2024-bull-dates.csv` |

Driver (example):

```bash
python scripts/backtest_mvp.py --ticker TCS.NS \
  --dates-csv results/dates-TCS-dec-2024-april-2025-bear-dates.csv
```

**Shared settings:** `PAPER_ABLATION=full`; **`initial_cash=100,000`**; **`zerodha_delivery`**, **`slippage_bps=0`**; anonymization on; LLM **`qwen/qwen3.5-flash-02-23`**. Logs: **`eval_results/dates-*-dates.log`**.

**Analysis:** **`scripts/backtest_regime_analysis.ipynb`**; figures: **`scripts/generate_paper_figures.py`**.

### 4.3 Results

**Table 1.** Agent vs buy-and-hold (frozen CSVs, $100,000 start). Sharpe is on **agent** daily equity (annualized[^sharpe252]; **no risk-free rate** subtracted).

| Ticker | Regime | Window | Days | B&H | Agent | B&H MDD | Agent MDD | Sharpe | B/H/S | Fees ($) |
|--------|--------|--------|------|-----|-------|---------|-----------|--------|-------|----------|
| RELIANCE | Bear | 2024-08-01 - 2025-01-03 | 111 | −17.43% | −7.54% | 21.0% | 5.11% | −3.12 | 7/28/76 | 1,010 |
| RELIANCE | Bull | 2025-01-01 - 2025-06-03 | 108 | +15.09% | +5.56% | 11.0% | 2.80% | −3.35 | 9/25/74 | 635 |
| TCS | Bear | 2024-12-02 - 2025-04-03 | 88 | −20.42% | −4.83% | 23.9% | 6.78% | −1.83 | 12/24/52 | 1,910 |
| TCS | Bull | 2024-06-03 - 2024-09-03 | 67 | +21.86% | +19.61% | 5.5% | 1.65% | +4.25 | 13/14/40 | 2,198 |

**Cross-ticker patterns.**

- **Bear (2/2):** agent **outperforms buy-and-hold** on total return (smaller loss) and shows **lower path drawdown** (e.g., RELIANCE bear: agent MDD 5.1% vs B&H MDD 21.0%). Both runs are **SELL-heavy** (52–76 SELL days), consistent with reduced long exposure during drawdowns.
- **Bull (mixed):** RELIANCE agent **lags** B&H (+5.6% vs +15.1%) with 74 SELL vs 9 BUY days—partial rally participation. TCS agent **nearly matches** B&H (+19.6% vs +21.9%) with more balanced activity (13 BUY, 40 SELL).
- **Sharpe:** negative in three of four runs—including RELIANCE bull (+5.6% return)—because daily equity volatility dominates on short windows; only TCS bull is Sharpe-positive (+4.25). We interpret Sharpe alongside total return and MDD, not in isolation.

**Table 2.** Selected outlook / stance shares (% of trading days). Full pivot in notebook.

| Ticker | Regime | market bullish | market bearish | bull stance buy | bear stance sell |
|--------|--------|----------------|----------------|---------------|------------------|
| RELIANCE | Bear | 10.8 | 31.5 | 100.0 | 88.3 |
| RELIANCE | Bull | 24.1 | 19.4 | 94.4 | 77.8 |
| TCS | Bear | 22.7 | 33.0 | 71.6 | 53.4 |
| TCS | Bull | 46.3 | 14.9 | 64.2 | 44.8 |

Internal **bull researcher** stances can remain buy-leaning while **final signals** stay defensive—downstream risk and trader stages drive executable actions.

### 4.4 Figures

```bash
MPLCONFIGDIR=.mpl_cache .venv/bin/python scripts/generate_paper_figures.py
```

- **`fig_regime_equity_grid`** — 2×2 agent vs B&H panels  
- **`fig_regime_returns_by_ticker`** — total return bars (four runs)  
- **`fig_regime_signals_by_ticker`** — BUY/HOLD/SELL counts  
- **`fig_regime_outlook_bullish`** — bullish analyst-outlook share heatmap  

---

## 5. Conclusion

We presented **Hindsight 20/20** and **multi-ticker regime-conditioned** evaluation on **RELIANCE.NS** and **TCS.NS**. The full pipeline shows **consistent relative protection in bear windows** and **heterogeneous bull-window outcomes**, with reproducible CSV artifacts.

**Limitations.** Two tickers; **different calendars per name**; one LLM; anonymization on but not ablated; Sharpe without a risk-free benchmark on short windows; no microstructure; Infosys windows planned but not run. Regimes are **exogenous**, not agent-predicted.

---

## Contributions

1. **Multi-agent decision graph** (S1 / M1).  
2. **Multi-ticker regime-conditioned evaluation** — four frozen runs, agent vs B&H (S2 / E1).  
3. **Structured stage outputs** (S3 / M3).  
4. **Point-in-time policy and anonymization** (S4 / M4–M5).  
5. **Backtest harness and artifacts** (S5 / M6).

**Not claimed:** SOTA returns; regime prediction; ablation studies in §4.

---

## Acknowledgements

The agent graph implementation builds on **TradingAgents** (Xiao et al., 2024; Tauric Research, Apache License 2.0). We thank the authors for open-sourcing the framework.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-05-29 | Multi-ticker Frozen E1: TCS + completed REL bull through 2025-06-03. |
