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

---

## Empirical claims

| ID | Claim | Evidence |
|----|--------|----------|
| E1 | The **full** pipeline (`PAPER_ABLATION=full`) on **two large-cap NSE listings** yields regime-dependent agent vs buy-and-hold outcomes under **per-ticker exogenous bear/bull windows** | Four frozen CSVs below + `scripts/backtest_regime_analysis.ipynb` |

---

## Regime definition (Frozen E1)

**Market regimes** are assigned **exogenously** per ticker from **buy-and-hold return on that ticker’s adjusted close** over each evaluation window (first → last processed trading day). Labels are independent of agent signals and of internal **Bull/Bear Researcher** debate roles.

| Label | Rule (per ticker, per window) |
|-------|-------------------------------|
| **Bear** | Underlying B&H return **≤ −10%** |
| **Bull** | Underlying B&H return **≥ +10%** |

**Calendar windows** are pre-specified in `regime-timeranges` **before** agent backtests. Windows **differ by ticker** because drawdowns and rallies are not synchronous. Each run uses **fresh $100,000** paper cash.

---

### Frozen E1 — four runs (two tickers × two regimes)

| Ticker | Regime | Calendar intent | Processed window | Days | Artifact CSV | Log |
|--------|--------|-----------------|------------------|------|--------------|-----|
| RELIANCE.NS | Bear | Aug 2024 – Jan 2025 | 2024-08-01 .. 2025-01-03 | 111 | `results/dates-REL-aug-2024-jan-2025-bear-dates.csv` | `eval_results/dates-REL-aug-2024-jan-2025-bear-dates.log` |
| RELIANCE.NS | Bull | Jan 2025 – Jun 2025 | 2025-01-01 .. 2025-06-03 | 108 | `results/dates-REL-jan-2025-june-2025-bull-dates.csv` | `eval_results/dates-REL-jan-2025-june-2025-bull-dates.log` |
| TCS.NS | Bear | Dec 2024 – Apr 2025 | 2024-12-02 .. 2025-04-03 | 88 | `results/dates-TCS-dec-2024-april-2025-bear-dates.csv` | `eval_results/dates-TCS-dec-2024-april-2025-bear-dates.log` |
| TCS.NS | Bull | Jun 2024 – Sep 2024 | 2024-06-03 .. 2024-09-03 | 67 | `results/dates-TCS-june-2024-sept-2024-bull-dates.csv` | `eval_results/dates-TCS-june-2024-sept-2024-bull-dates.log` |

**Shared protocol:** `PAPER_ABLATION=full`; `initial_cash=$100,000`; `cost_model=zerodha_delivery`, `slippage_bps=0`; anonymization enabled; LLM `qwen/qwen3.5-flash-02-23`; driver `scripts/backtest_mvp.py --dates-csv <artifact>`.

### Frozen metrics (Table 1 source)

| Ticker | Regime | B&H return | Agent return | B&H MDD | Agent MDD | Sharpe | BUY / HOLD / SELL | Fees ($) |
|--------|--------|------------|--------------|---------|-----------|--------|-------------------|----------|
| RELIANCE | Bear | −17.43% | −7.54% | 21.0% | 5.11% | −3.12 | 7 / 28 / 76 | 1,010.32 |
| RELIANCE | Bull | +15.09% | +5.56% | 11.0% | 2.80% | −3.35 | 9 / 25 / 74 | 635.44 |
| TCS | Bear | −20.42% | −4.83% | 23.9% | 6.78% | −1.83 | 12 / 24 / 52 | 1,909.83 |
| TCS | Bull | +21.86% | +19.61% | 5.5% | 1.65% | +4.25 | 13 / 14 / 40 | 2,197.78 |

**B&H MDD:** peak-to-trough on buy-and-hold equity from the same adjusted closes in each schedule CSV (`max_drawdown` on `$100{,}000 × close/close_0$`). **Sharpe:** agent daily equity only; annualized $\sqrt{252}$ (252 trading days/year, US convention; NSE ≈ 240–250; retained for comparability); no risk-free rate subtracted.

**Cross-ticker summary:** In **both bear windows**, agent return exceeds buy-and-hold (smaller loss) and agent MDD is **substantially below** B&H MDD. In **bull windows**, outcomes **diverge**: RELIANCE agent lags B&H; TCS agent nearly tracks B&H. Sharpe is negative in three of four runs despite positive total return in one of them (RELIANCE bull).

**Analysis / figures:** `scripts/backtest_regime_analysis.ipynb`, `scripts/generate_paper_figures.py` → `fig_regime_equity_grid`, `fig_regime_returns_by_ticker`, `fig_regime_signals_by_ticker`, `fig_regime_outlook_bullish`.

**Retired:** `results/_retired/` (ablation CSVs, old longitudinal `dates.csv`).

**Planned but not in §4:** Infosys windows in `regime-timeranges` (not run).

---

## Forbidden in camera-ready unless you have proof

- Regime labels from agent outlook columns.
- “Same calendar across tickers” (windows are per-ticker).
- SOTA or regime-prediction claims.

---

## Changelog

| Date | Note |
|------|------|
| 2026-05-28 | Initial regime freeze (RELIANCE only). |
| 2026-05-29 | **Multi-ticker Frozen E1:** REL bull completed through 2025-06-03; TCS bear + bull added. |
