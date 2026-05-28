---
title: "Point-in-Time Multi-Agent LLM Trading: A Reproducible LangGraph Stack with Regime-Conditioned Evaluation and Fair Backtesting"
author: "[Rohit Edward Martires] (Independent researcher, [Goa, India]). Email: [rohitmartires14@gmail.com]."
date: 28 May 2026
geometry: margin=1in
fontsize: 12pt
documentclass: article
numbersections: true
abstract: |
  Large language models are increasingly used in financial decision pipelines, yet published agent stacks are often hard to reproduce and rarely evaluated under distinct market conditions on historical as-of dates. We present **Hindsight 20/20**, an open **LangGraph** stack for single-asset trading with structured **Pydantic** outputs, a **simulation end date** for point-in-time data, optional **ticker anonymization**, and a fee-aware **paper backtest**. We evaluate the **full** pipeline on **RELIANCE.NS** in two **exogenous** windows—a **bear regime** (underlying return −17.4%, Aug 2024–Jan 2025) and a **bull regime** (+19.3%, Jan–May 2025)—each from $100,000 paper cash. The agent loses less than buy-and-hold in the bear window (−7.5% vs −17.4%) but captures less of the rally in the bull window (+8.7% vs +19.3%). Frozen CSV artifacts and scripts reproduce tables and figures.
header-includes:
  - \usepackage{setspace}
  - \doublespacing
  - \usepackage{graphicx}
  - \usepackage{amsmath}
---

**Keywords:** algorithmic trading; large language models; multi-agent systems; reproducibility; point-in-time data; market regimes.

## Introduction

Researchers are experimenting with large language models (LLMs) inside trading workflows. Building research-grade stacks remains difficult: temporal constraints are often implicit, and evaluations rarely ask how the **same** implementation behaves when the **underlying trend** differs.

We present **Hindsight 20/20**, an open **LangGraph** implementation focused on reproducibility and auditable evaluation. **Structured outputs**, optional **anonymization**, and a **simulation end date** bound data access. A **paper backtest** replays signals with configurable fees.

We evaluate the **full** pipeline (`PAPER_ABLATION=full`) on **RELIANCE.NS** in two **independent** backtests over calendar windows labeled **bear** and **bull** from exogenous underlying returns (Section 4.1). Section 2 surveys related work; Section 3 the system; Section 4 results; Section 5 concludes; Section 6 lists contributions.

## Related Work

**LLM agents for trading.** Multi-agent frameworks orchestrate specialist roles (Xiao et al., 2024; Yu et al., 2023; Yang et al., 2023). We emphasize **reproducible systems engineering**: one codepath, schema-constrained outputs, temporal controls, and scriptable backtests tied to CSV artifacts.

**Point-in-time data and leakage.** We treat a simulation end date, vendor routing, and optional anonymization as first-class requirements.

**Robustness across market conditions.** We contribute a **regime-split** evaluation on one ticker—exogenous bear/bull labels, not regime prediction.

**Execution realism.** A paper ledger with stated fees links decisions to P&L without microstructure simulation.

## Method / System

**Architecture.** `TradingAgentsGraph` wires analysts, **Bull/Bear Researcher** debate roles (internal agents—not market-regime labels), trader, and risk stages. **`run_backtest_mvp`** uses the same graph as interactive runs.

**Structured outputs, PIT policy, anonymization.** Pydantic schemas with fallbacks; simulation-date clamps; optional `TickerMapper`. Frozen E1 runs used anonymization.

**Pipeline configuration.** Section 4 uses **`PAPER_ABLATION=full`** (default): all analysts, investment debate, risk phase. Other presets exist for internal use only.

**Backtest.** `scripts/backtest_mvp.py --dates-csv` writes schedule CSVs with signals, equity, and outlook columns.

## Experiments

### Goals and regime definition

**Market regimes** are assigned **exogenously** from underlying **RELIANCE.NS** buy-and-hold return over each window: **bear** if return <= -10%; **bull** if >= +10%. Each run starts from **$100,000** fresh cash.

### Protocol

| Regime | Processed window | Artifact CSV |
|--------|------------------|--------------|
| Bear | 2024-08-01 .. 2025-01-03 | `results/dates-REL-aug-2024-jan-2025-bear-dates.csv` |
| Bull | 2025-01-01 .. 2025-05-16 | `results/dates-REL-jan-2025-june-2025-bull-dates.csv` |

Shared: `PAPER_ABLATION=full`; `zerodha_delivery`; `slippage_bps=0`; LLM **`qwen/qwen3.5-flash-02-23`**. Bull schedule targets June 2025 but the frozen artifact ends **2025-05-16** (API limits).

### Results

**Table 1.** Agent vs buy-and-hold ($100,000 start).

| Regime | Days | B&H | Agent | End equity | Max DD | Sharpe | B/H/S signals | Fees ($) |
|--------|------|-----|-------|------------|--------|--------|---------------|----------|
| Bear | 111 | −17.43% | −7.54% | 92,459.38 | 5.11% | −3.12 | 7/28/76 | 1,010.32 |
| Bull | 94 | +19.25% | +8.68% | 108,675.02 | 0.47% | +2.62 | 6/20/68 | 613.69 |

In the bear window the agent **outperforms buy-and-hold** with a defensive SELL-heavy profile; in the bull window it **underperforms** despite positive return—partial rally participation only.

**Table 2.** Selected outlook / stance shares (% of days).

| Regime | Field | bullish | bearish | mixed | buy | sell | hold |
|--------|-------|---------|---------|-------|-----|------|------|
| Bear | market_outlook | 10.8 | 31.5 | 48.6 | — | — | — |
| Bear | bull_implied_stance | — | — | — | 100.0 | — | — |
| Bear | bear_implied_stance | — | — | — | — | 88.3 | 10.8 |
| Bull | market_outlook | 21.3 | 21.3 | 46.8 | — | — | — |
| Bull | bull_implied_stance | — | — | — | 97.9 | — | 1.1 |
| Bull | bear_implied_stance | — | — | — | — | 85.1 | 12.8 |

### Figures

![Figure 1. Agent vs buy-and-hold equity by regime.](figures/fig_regime_equity.pdf)

![Figure 2. Total return by regime.](figures/fig_regime_returns.pdf)

![Figure 3. Final signal counts by regime.](figures/fig_regime_signals.pdf)

![Figure 4. Share of days with bullish analyst outlook.](figures/fig_regime_outlook_bullish.pdf)

## Conclusion

We presented an open LangGraph trading stack and **regime-conditioned** evaluation on **RELIANCE.NS**. The full pipeline shows asymmetric behavior: relative protection in the bear window and partial participation in the bull window.

**Limitations.** One ticker; bull run truncated at 2025-05-16; single LLM; regimes are exogenous, not predicted by the agent.

## Contributions

1. **Multi-agent decision graph** (S1).
2. **Regime-conditioned evaluation** with frozen bear/bull CSVs (S2).
3. **Structured stage outputs** (S3).
4. **Point-in-time policy and anonymization** (S4).
5. **Backtest harness and analysis artifacts** (S5).

## Acknowledgements {.unnumbered}

Not applicable.

## References {.unnumbered}

Xiao, Y., Sun, E., Luo, D. and Wang, W., 2024. TradingAgents: Multi-Agents LLM Financial Trading Framework. *arXiv preprint* arXiv:2412.20138 [q-fin.TR]. Available at: https://arxiv.org/abs/2412.20138 (Accessed: 28 May 2026).

Yang, H., Liu, X.-Y. and Wang, C.D., 2023. FinGPT: Open-Source Financial Large Language Models. *arXiv preprint* arXiv:2306.06031 [q-fin.ST]. Available at: https://arxiv.org/abs/2306.06031 (Accessed: 28 May 2026).

Yu, Y., Li, H., Chen, Z., Jiang, Y., Li, Y., Zhang, D., Liu, R., Suchow, J.W. and Khashanah, K., 2023. FinMem: A Performance-Enhanced LLM Trading Agent with Layered Memory and Character Design. *arXiv preprint* arXiv:2311.13743 [q-fin.CP]. Available at: https://arxiv.org/abs/2311.13743 (Accessed: 28 May 2026).
