---
title: "Point-in-Time Multi-Agent LLM Trading: A Reproducible LangGraph Stack with Regime-Conditioned Evaluation and Fair Backtesting"
author: "[Rohit Edward Martires] (Independent researcher, [Goa, India]). Email: [rohitmartires14@gmail.com]."
date: 29 May 2026
geometry: margin=1in
fontsize: 12pt
documentclass: article
numbersections: true
abstract: |
  Large language models are increasingly used in financial decision pipelines, yet published agent stacks are often hard to reproduce and rarely evaluated under distinct market conditions on historical as-of dates. We present **Hindsight 20/20**, an open **LangGraph** stack with structured **Pydantic** outputs, point-in-time data access, optional **ticker anonymization**, and a fee-aware **paper backtest**. We evaluate the **full** pipeline on **RELIANCE.NS** and **TCS.NS** in **exogenous bear and bull windows** (per-ticker underlying return at most -10% or at least +10%), each from $100,000 paper cash. In **both bear windows**, the agent loses less than buy-and-hold; in **bull windows**, outcomes diverge (RELIANCE lags B&H; TCS nearly tracks it). Frozen CSV artifacts reproduce tables and figures.
header-includes:
  - \usepackage{setspace}
  - \doublespacing
  - \usepackage{graphicx}
  - \usepackage{amsmath}
---

**Keywords:** algorithmic trading; large language models; multi-agent systems; reproducibility; point-in-time data; market regimes.

## Introduction

Researchers are experimenting with LLMs inside trading workflows, but rarely report how the **same stack** behaves across **different underlying trends** or **more than one issuer**. We present **Hindsight 20/20**, an open **LangGraph** implementation with structured outputs, optional anonymization, a simulation end date, and a paper backtest. We evaluate the **full** pipeline on **RELIANCE.NS** and **TCS.NS** in four independent runs (bear and bull per ticker). Section 2 surveys related work; Section 3 the system; Section 4 results; Section 5 concludes; Section 6 lists contributions.

## Related Work

**LLM trading agents** motivate multi-role graphs (Xiao et al., 2024; Yu et al., 2023; Yang et al., 2023). We emphasize reproducible engineering: one codepath, schema-constrained outputs, temporal controls, CSV artifacts.

**Point-in-time data and leakage** require explicit simulation horizons and optional anonymization.

**Regime-split evaluation** on the same implementation is uncommon; we report four frozen runs with **per-ticker calendars**, not regime prediction.

**Execution realism** via a paper ledger with stated fees.

## Method / System

**TradingAgentsGraph** composes analysts, bull/bear **debate roles** (internal agents, distinct from market regimes), trader, and risk. Section 4 uses **`PAPER_ABLATION=full`**. **`backtest_mvp.py --dates-csv`** produces wide schedule CSVs.

## Experiments

### Regime definition

For each ticker, calendar windows in **`regime-timeranges`** are labeled **bear** if underlying buy-and-hold return is at most **-10%**, **bull** if at least **+10%** over the processed window. Each run starts from **$100,000** fresh cash. Windows differ by ticker.

### Protocol and results

**Table 1.** Four frozen runs.

| Ticker | Regime | Window | Days | B&H | Agent | End equity | B/H/S |
|--------|--------|--------|------|-----|-------|------------|-------|
| RELIANCE | Bear | 2024-08-01 .. 2025-01-03 | 111 | -17.4% | -7.5% | 92,459 | 7/28/76 |
| RELIANCE | Bull | 2025-01-01 .. 2025-06-03 | 108 | +15.1% | +5.6% | 105,559 | 9/25/74 |
| TCS | Bear | 2024-12-02 .. 2025-04-03 | 88 | -20.4% | -4.8% | 95,166 | 12/24/52 |
| TCS | Bull | 2024-06-03 .. 2024-09-03 | 67 | +21.9% | +19.6% | 119,607 | 13/14/40 |

**Bear (2/2):** agent loses less than buy-and-hold. **Bull:** RELIANCE lags B&H; TCS nearly tracks B&H. Final signals remain SELL-heavy in most runs.

### Figures

![Figure 1. Agent vs buy-and-hold equity (2x2 grid).](figures/fig_regime_equity_grid.pdf)

![Figure 2. Total returns (four runs).](figures/fig_regime_returns_by_ticker.pdf)

![Figure 3. Signal counts.](figures/fig_regime_signals_by_ticker.pdf)

![Figure 4. Bullish analyst-outlook share.](figures/fig_regime_outlook_bullish.pdf)

## Conclusion

We presented an open LangGraph stack and **multi-ticker regime-conditioned** evaluation. Bear windows show relative downside protection; bull outcomes are heterogeneous. **Limitations:** two tickers, per-ticker calendars, one LLM.

## Contributions

1. Multi-agent decision graph.
2. Multi-ticker regime-conditioned evaluation (four frozen CSVs).
3. Structured stage outputs.
4. Point-in-time policy and anonymization.
5. Backtest harness and analysis artifacts.

## Acknowledgements {.unnumbered}

Not applicable.

## References {.unnumbered}

Xiao, Y., Sun, E., Luo, D. and Wang, W., 2024. TradingAgents: Multi-Agents LLM Financial Trading Framework. *arXiv preprint* arXiv:2412.20138 [q-fin.TR]. Available at: https://arxiv.org/abs/2412.20138 (Accessed: 29 May 2026).

Yang, H., Liu, X.-Y. and Wang, C.D., 2023. FinGPT: Open-Source Financial Large Language Models. *arXiv preprint* arXiv:2306.06031 [q-fin.ST]. Available at: https://arxiv.org/abs/2306.06031 (Accessed: 29 May 2026).

Yu, Y., Li, H., Chen, Z., Jiang, Y., Li, Y., Zhang, D., Liu, R., Suchow, J.W. and Khashanah, K., 2023. FinMem: A Performance-Enhanced LLM Trading Agent with Layered Memory and Character Design. *arXiv preprint* arXiv:2311.13743 [q-fin.CP]. Available at: https://arxiv.org/abs/2311.13743 (Accessed: 29 May 2026).
