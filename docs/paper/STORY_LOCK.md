# Story lock (memory-aligned)

**Last updated:** 2026-05-29.

---

## Title and pitch

**Working title:** *Point-in-Time Multi-Agent LLM Trading: A Reproducible LangGraph Stack with Regime-Conditioned Evaluation and Fair Backtesting*

**One-line pitch:** Open **LangGraph** stack with structured outputs, point-in-time data, optional anonymization, and fee-aware backtest; §4 evaluates the **full** pipeline on **RELIANCE.NS** and **TCS.NS** under **per-ticker exogenous bear/bull windows** with agent vs buy-and-hold comparison.

---

## Contributions

| ID | Contribution | Grounding |
|----|----------------|-----------|
| **S1** | Multi-agent decision graph | `tradingagents-graph`, `tradingagents-agents` |
| **S2** | **Multi-ticker regime-conditioned evaluation** (four frozen runs) | `scripts/backtest_mvp.py`, `backtest_regime_analysis.ipynb`, Frozen E1 |
| **S3** | Structured stage outputs | `tradingagents-schemas`, `tradingagents-llm-clients` |
| **S4** | PIT data + optional anonymization | `tradingagents-dataflows`, `tradingagents-anonymization` |
| **S5** | Backtest harness + CSV artifacts | `tradingagents-backtest`, `scripts` |

---

## Empirical headline (honest)

- **Bear (2/2):** agent loses less than B&H (RELIANCE, TCS).
- **Bull (mixed):** RELIANCE agent lags B&H; TCS agent nearly tracks B&H.
- **Not claimed:** regime prediction, SOTA returns, shared calendar across tickers.

---

## Figures

| Figure | File |
|--------|------|
| 2×2 equity grid | `fig_regime_equity_grid` |
| Returns by run | `fig_regime_returns_by_ticker` |
| Signal counts | `fig_regime_signals_by_ticker` |
| Bullish outlook heatmap | `fig_regime_outlook_bullish` |
