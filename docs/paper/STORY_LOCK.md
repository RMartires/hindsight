# Story lock (memory-aligned)

**Last updated:** 2026-05-29.

---

## Title and pitch

**Working title:** *Point-in-Time Multi-Agent LLM Trading: A Reproducible LangGraph Stack with Regime-Conditioned Case Study Evaluation and Fair Backtesting*

**One-line pitch:** Open **LangGraph** stack (structured outputs, PIT data, anonymization, fee-aware backtest); §4 is an **illustrative four-window case study** on **RELIANCE.NS** and **TCS.NS** (N=1 per window), not a multi-seed universe benchmark.

---

## What this paper is / is not

| Is | Is not |
|----|--------|
| Reproducible systems + frozen artifacts | SOTA / universe alpha proof |
| PIT policy + schema audit trail | Regime prediction |
| Net returns after Zerodha fees | Multi-seed statistical benchmark |
| Honest scoped case study (4 windows) | Cherry-picked performance claim |

---

## Contributions (priority order)

| ID | Contribution | Grounding |
|----|----------------|-----------|
| **S5** | Backtest harness + CSV replication packet | `tradingagents-backtest`, `scripts` |
| **S4** | PIT data + optional anonymization | `tradingagents-dataflows`, `tradingagents-anonymization` |
| **S3** | Structured stage outputs | `tradingagents-schemas`, `tradingagents-llm-clients` |
| **S1** | Multi-agent graph + tool-bound analyst tasks | `tradingagents-graph`, `tradingagents-agents` |
| **S2** | Regime-conditioned case study (4 windows, documented limits) | Frozen E1, `backtest_regime_analysis.ipynb` |

---

## Empirical headline (honest)

- **Bear (2/2):** agent loses less than B&H; lower MDD (both names).
- **Bull (mixed):** REL lags B&H (architectural boundary); TCS nearly tracks B&H.
- **N=1** per regime window; no seed variance.
- **Not claimed:** regime prediction, SOTA returns, shared calendar, index universe.

---

## Figures

| Figure | File |
|--------|------|
| 2×2 equity grid | `fig_regime_equity_grid` |
| Returns by run | `fig_regime_returns_by_ticker` |
| Signal counts | `fig_regime_signals_by_ticker` |
| Bullish outlook heatmap | `fig_regime_outlook_bullish` |
