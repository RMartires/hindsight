# Manuscript (draft — export to PDF / LaTeX)

**Purpose:** Submission-facing prose only. Scope: [paper-roadmap.md](paper-roadmap.md). Claims: **`.cursor/memory.md`** and [claim-evidence-map.md](claim-evidence-map.md).

**Last updated:** 2026-05-29.

**PDF:** `pandoc docs/paper/manuscript.md -o paper-draft.pdf --pdf-engine=tectonic`. IOS: `./docs/paper/submission/build_ios_package.sh`.

---

## Working title

*Point-in-Time Multi-Agent LLM Trading: A Reproducible LangGraph Stack with Regime-Conditioned Case Study Evaluation and Fair Backtesting*

---

## Abstract

Large language models are increasingly used in financial decision pipelines, yet published agent stacks are often hard to reproduce, rarely enforce temporal data boundaries, and seldom report net returns after transaction costs. We present **Hindsight 20/20**, an open **LangGraph** stack with structured **Pydantic** outputs, a **simulation end date** for point-in-time data, optional **ticker anonymization**, and a fee-aware **paper backtest**. The primary contribution is **reproducible systems engineering**—one codepath, auditable stage artifacts, and frozen CSV schedules—not a universe-scale alpha benchmark. As an **illustrative case study**, we evaluate the **full** pipeline on two liquid large-cap NSE listings—**RELIANCE.NS** and **TCS.NS**—in **four pre-specified regime windows** (two tickers × exogenous bear/bull labels; **one deterministic trajectory per window**, no seed averaging). In **both bear windows**, the agent loses **less** than buy-and-hold on total return and shows **lower path drawdown** (RELIANCE: −7.5% vs −17.4%, MDD 5.1% vs 21.0%; TCS: −4.8% vs −20.4%, MDD 6.8% vs 23.9%). In **bull windows**, outcomes **diverge**: RELIANCE lags buy-and-hold (+5.6% vs +15.1%) while TCS nearly tracks it (+19.6% vs +21.9%). We interpret heterogeneous bull outcomes as an **architectural boundary** of defensive multi-stage coordination rather than a performance claim. Frozen CSV artifacts and scripts reproduce tables and figures. **Code and artifacts:** [https://github.com/RMartires/hindsight](https://github.com/RMartires/hindsight).

*(IOS submission: [`docs/paper/submission/`](submission/) — run `build_ios_package.sh`.)*

---

## 1. Introduction

Researchers are experimenting with large language models (LLMs) inside trading workflows amid a rapid expansion of LLM-driven agent systems (Bădică et al., 2025). Yet evaluations rarely ask how the **same implementation** behaves when the **underlying trend** differs, rarely enforce point-in-time data access at the adapter layer, and rarely report **net** returns after stated transaction costs.

**What this paper is.** **Hindsight 20/20** extends the open-source **TradingAgents** multi-agent LangGraph framework (Xiao et al., 2024) with (i) schema-constrained stage outputs, (ii) a simulation end date for point-in-time vendor queries, (iii) optional ticker anonymization, and (iv) a scriptable, fee-aware paper backtest tied to **frozen CSV artifacts**. We document **how** to build and audit such a stack and provide an **honest, scoped** regime-split case study on two names.

**What this paper is not.** We do **not** claim state-of-the-art risk-adjusted returns, regime *prediction*, or statistical generalization from a broad equity universe. We do **not** report multi-seed variance (each regime window is **N=1**). Frontier empirical papers (e.g., Jeon and Lee, 2026; Miyazaki et al., 2026) average tens of random seeds across index universes; our evaluation scope is deliberately narrower and is labeled as such (§4.1, Table 3).

**Case-study evaluation.** We run the **full** pipeline (`PAPER_ABLATION=full`) on **RELIANCE.NS** and **TCS.NS**. For each ticker we pre-specify one **bear** and one **bull** calendar window in **`regime-timeranges`** before any agent run; labels follow exogenous underlying buy-and-hold thresholds (§4.2). Each of **four regime windows** starts from **$100,000** fresh paper cash; we compare agent **net** return to **buy-and-hold** on the same window.

**Code.** Implementation, frozen evaluation CSVs, and figure scripts: [https://github.com/RMartires/hindsight](https://github.com/RMartires/hindsight).

**Structure.** §2 related work; §3 system; §4 case study evaluation; §5 conclusion; **Contributions** at the end.

---

## 2. Related Work

*Bibliography: [bib-seed.bib](bib-seed.bib).*

**LLM agents and classic MAS.** Multi-agent frameworks orchestrate specialist roles for trading and finance (Xiao et al., 2024; Yu et al., 2023; Yang et al., 2023). Bădică et al. (2025) situate this wave as a shift from explicitly programmed BDI-style agents to emergent LLM behaviors—raising new demands for verifiable coordination and audit trails. While **TradingAgents** (Xiao et al., 2024) provides the foundational analyst → debate → trader graph that we extend, it does not ship adapter-level temporal clamps, schema-persisted stage artifacts, or a fee-aware replication harness. **AlphaAgents** (Zhao et al., 2025) validates institution-style role separation (Fundamental, Sentiment, Valuation) with structured debate; **QuantAgents** (Li et al., 2025) emphasizes manager-led **meetings** and simulated-trading feedback—both comparators for our Bull/Bear debate loop, but neither foregrounds point-in-time vendor routing or frozen schedule CSVs as first-class outputs.

**Methodological standards, leakage, and overfitting.** Nguyen and Pham (2026) survey LLM financial multi-agent systems and propose **Consolidated Minimum Standards**, documenting pervasive evaluation failures—look-ahead bias, transaction-cost neglect, and regime-shift blindness—that can reverse the sign of reported returns. They introduce the **Coordination Breakeven Spread (CBS)** for asking whether multi-agent coordination pays for its turnover cost; we report a simplified fee-and-turnover breakeven in §4.5 and defer full latency CBS to future work. Bailey et al. (2014) show that undisclosed configuration search makes strong in-sample backtests statistically cheap to manufacture; Hindsight responds with **pre-specified** windows in `regime-timeranges`, frozen artifacts, and explicit N=1 scope rather than implied generalization.

**Point-in-time policy and anonymization.** Early LLM trading papers often relied on prompt-level “do not peek” instructions. Nguyen and Pham (2026) treat **contamination control** and **net-of-cost returns** as minimum standards; Hindsight implements the former via a **simulation end date** at vendor routing (**M4**) and the latter via a **Zerodha delivery** paper ledger. Jeon and Lee (2026) (**BlindTrade**) provide the strongest anonymization-first defense: tickers like “AAPL” can trigger memorized pretraining associations rather than fresh reasoning; they anonymize S&P 500 constituents daily and report Sharpe 1.40 ± 0.22 across **20 seeds**. Hindsight’s optional **`STOCK_####`** aliases (§3.5) pursue the same goal within a LangGraph replication stack; we do not ablate anonymization in §4.

**Fine-grained tasks and coordination topology.** Miyazaki et al. (2026) show that **fine-grained** analyst tasks (e.g., explicit ratio and indicator computations) outperform coarse “analyze fundamentals” prompts under leakage-controlled TOPIX-style evaluation with **50 trials**. Our market and fundamentals analysts are **tool-bound** to concrete fetches and Tier-1 indicators (§3.2)—aligning architecture with that finding without claiming comparable universe-scale statistics. Dewansh (2026) frames **explainable stability** and **rationale persistence** as audit criteria for orchestrated trading agents; our Pydantic stage outputs and wide schedule CSVs are designed to support that traceability (outlook → stance → `final_signal`), even though we do not formally score policy convergence.

**Benchmarks, simulators, and live evaluation.** Qian et al. (2026) introduce the **Agent Market Arena (AMA)**, a lifelong multi-market benchmark showing that **agent architecture** often matters more than LLM backbone choice—a motivation for holding the model fixed (`qwen/qwen3.5-flash-02-23`) and varying regime context in §4. Papadakis et al. (2025) (**StockSim**) define order-level simulation with latency, slippage, and limit-order-book microstructure; our paper ledger is candlestick-level with stated fees and **no LOB claim**, treating StockSim-class realism as aspirational future work.

**Empirical scope vs frontier benchmarks.** Jeon and Lee (2026), Li et al. (2025), and Miyazaki et al. (2026) optimize for **statistical stress tests** across index universes, seeds, or simulated meetings. Hindsight optimizes for **auditability and temporal integrity** on a two-ticker, four-window case study (Table 3)—complementary, not directly comparable on seeds or universe breadth.

**Positioning summary.** Where **TradingAgents** supplies the graph skeleton and **BlindTrade** / Nguyen and Pham (2026) articulate *what to measure*, Hindsight 20/20 implements *how to reproduce it*: simulation end dates, structured artifacts, optional anonymization, net returns, and frozen CSV schedules that regenerate Tables 1–4 without rerunning LLM inference.

---

## 3. Method / System

Pointers: **`.cursor/memory.md`**.

### 3.1 Architecture

**`TradingAgentsGraph`**: analysts → **Bull/Bear Researcher** debate (*internal roles*, not §4 market regimes) → trader → risk → final decision. Core routing follows **TradingAgents** (Xiao et al., 2024); our modifications focus on temporal data policy, schema-constrained outputs, and the backtest/evaluation pipeline below. Same graph for **`run_backtest_mvp`**.

### 3.2 Analyst task decomposition

Each analyst role is bound to **specific tools** and emits a structured **`AnalystReport`** (outlook + narrative). This supports traceable rationale from raw data to downstream debate—not coarse role labels alone.

| Stage | Agent | Tools (representative) | Concrete tasks |
|-------|--------|------------------------|----------------|
| Market | Market analyst | `get_stock_data`, `get_indicators` | Fetch OHLCV; select up to **8 complementary Tier-1 indicators** (trend: 50/200 SMA, 10 EMA, MACD; momentum: RSI; volatility: Bollinger, ATR; volume: VWMA, MFI) with non-redundant justification |
| Fundamentals | Fundamentals analyst | `get_fundamentals`, `get_balance_sheet`, `get_cashflow`, `get_income_statement` | Pull statements and issuer profile; analyze revenue, margins, balance-sheet trends |
| News | News analyst | `get_news`, `get_global_news` | Company-targeted and macro news over a rolling window |
| Sentiment | Social-media analyst | `get_news` (company/social queries) | Sentiment and social discussion synthesis |
| Debate | Bull / Bear researchers | — (read analyst reports) | Argue buy vs sell thesis from shared evidence |
| Execution | Trader, Risk manager | — | Propose and gate **BUY/HOLD/SELL** |

Structured fields (`market_outlook`, `fundamentals_outlook`, `bull_implied_stance`, `final_signal`, etc.) are persisted in schedule CSVs for audit (**M3**), supporting **explainable stability** in the sense of Dewansh (2026): a coherent trace from evidence to executable action.

### 3.3 Tools and structured outputs

Analyst tool calls respect the simulation end date; stage outputs conform to **Pydantic** schemas (`tradingagents/schemas/outputs.py`, **M3**).

### 3.4 Point-in-time data policy

A **simulation end date** clamps vendor queries so agents cannot access data after the as-of trade date (**M4**).

### 3.5 Ticker anonymization

LLMs trained on public text encode firm-specific narratives tied to ticker symbols. In a point-in-time backtest, that **pretraining leakage** can bias decisions.

Hindsight optionally **anonymizes the issuer** for all LLM-facing prompts and tool outputs (**M5**):

1. **Deterministic ticker aliases** — `TickerMapper.for_real_ticker()` maps each real symbol to a stable synthetic id (`STOCK_####`, SHA-256–derived).
2. **Round-trip vendor access** — tool wrappers call `resolve_ticker_for_vendor()` before API calls, then `scrub_ticker_text()` on responses.
3. **News scrubbing** — `scrub_news_text()` replaces multi-word proper nouns with `PROPER_NOUN` placeholders (heuristic, news-only).

Frozen E1 uses **`enable_anonymization=True`**. We do **not** ablate anonymization in §4.

### 3.6 Backtest metrics

The paper ledger (`tradingagents/backtest/`) records daily agent equity **after fees**. Primary §4 metrics emphasize **total return**, **maximum drawdown (MDD)**, and **fee drag**; risk-adjusted ratios are secondary on short windows (67–111 trading days).

| Metric | Definition |
|--------|------------|
| **Total return (net)** | \((V_T - V_0) / V_0\) on agent equity after fees |
| **Gross return** | Net return plus fees as a fraction of \(V_0\) |
| **Fee drag** | Gross return minus net return |
| **Alpha vs B&H** | Agent net return minus buy-and-hold return on the same adjusted closes |
| **Max drawdown (MDD)** | Peak-to-trough on agent equity; **B&H MDD** on \(V_0 \times \text{close}/\text{close}_0\) |
| **Excess Sharpe ratio** | Mean daily excess return (over risk-free) / stdev, × \(\sqrt{252}\)[^sharpe252] |
| **Sortino / Calmar** | Implemented; reported in Table 2 (secondary) |

[^sharpe252]: Annualization uses 252 trading days (US convention). NSE calendars are ≈240–250 days; we retain 252 for comparability. **Risk-free rate:** India short-rate proxy **6.5% p.a.**, converted to a daily rate \(r_f/252\), applied uniformly across windows (post-hoc on frozen equity series). Qualitative conclusions are unchanged under a ±1% p.a. sensitivity band.

### 3.7 Pipeline configuration

§4 uses **`PAPER_ABLATION=full`**. Presets **`a1`–`a3`** exist for internal use only (**M2**).

### 3.8 Paper backtest and replication packet

**`scripts/backtest_mvp.py --dates-csv`** writes wide schedule CSVs (signals, equity, outlook, stance, and running metrics).

**Replication packet (Frozen E1):** four schedule CSVs under **`results/dates-*-dates.csv`**, matching logs under **`eval_results/`**, pre-specified windows in **`regime-timeranges`**, shared env (`PAPER_ABLATION=full`, `initial_cash=100000`, `cost_model=zerodha_delivery`, `slippage_bps=0`, anonymization on, LLM `qwen/qwen3.5-flash-02-23`). Tables and figures regenerate via **`scripts/backtest_regime_analysis.ipynb`** and **`scripts/generate_paper_figures.py`**.

### 3.9 Observability

Langfuse optional; not empirical evidence.

---

## 4. Case Study Evaluation

### 4.1 Evaluation scope and inferential limits

| Dimension | This study | Typical frontier benchmark |
|-----------|------------|----------------------------|
| **Universe** | 2 liquid NSE large-caps (RELIANCE, TCS) | Index constituents (e.g., S&P 500, TOPIX 100) |
| **Regime windows** | 4 pre-specified (2 tickers × bear/bull) | Full sample or rolling panels |
| **Stochasticity** | **N=1 trajectory per window** (no seed variance) | 20–50 independent trials |
| **Regime labels** | Exogenous from underlying B&H (±10%) | Often endogenous or undisclosed |
| **Bias control** | Simulation end date + optional anonymization | Strict anonymization (BlindTrade) |
| **Costs** | Stated delivery fees (net returns) | Often gross returns |

We treat §4 as an **illustrative stress test** of one stack under contrasting underlying trends—not a hypothesis test about expected alpha. Outcomes **observed in these four windows** should not be extrapolated to a broad universe without further study (§5).

**Pre-specification.** Calendar windows are listed in **`regime-timeranges`** **before** agent backtests. Regime labels are assigned **exogenously** from underlying buy-and-hold return and are **independent** of internal Bull/Bear Researcher debate roles.

### 4.2 Regime definition and protocol

| Regime label | Rule (underlying B&H on processed window, per ticker) |
|--------------|--------------------------------------------------------|
| **Bear** | Total return **≤ −10%** |
| **Bull** | Total return **≥ +10%** |

Windows **differ by ticker** (e.g., TCS bull Jun–Sep 2024; RELIANCE bull Jan–Jun 2025). Each run uses **$100,000** initial cash.

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

**Frozen artifacts:** [claim-evidence-map.md](claim-evidence-map.md) (**Frozen E1**).

### 4.3 Positioning vs prior agent-trading systems

**Table 3.** Qualitative comparison (see §4.1 for scope limits).

| Feature | Hindsight 20/20 | BlindTrade | QuantAgents | Expert Investment Teams |
|---------|-----------------|------------|-------------|-------------------------|
| Primary goal | Reproducible PIT stack + audit trail | Anonymized RL/GNN policy | Simulated agent meetings | Hierarchical analyst teams |
| Architecture | LangGraph (staged) | GNN + RL | Meeting simulation | Manager–analyst hierarchy |
| Stochasticity reported | N=1 per regime window | 20 seeds | Multi-year + live tracking | 50 trials |
| Universe | 2 NSE large-caps | S&P 500 (PIT) | Multi-asset simulation | TOPIX 100 |
| Bias control | Sim. end date + opt. anonymization | Strict anonymization | Simulation feedback | Knowledge cutoff controls |
| Costs in backtest | Net (Zerodha delivery) | Varies | Varies | Varies |
| Key §4 metrics | Return, MDD, fee drag | Sharpe (mean ± std) | ARR, volatility | Median Sharpe |

### 4.4 Results

**Table 1.** Agent vs buy-and-hold (frozen CSVs, $100,000 start). **Primary metrics:** net return, MDD, alpha vs B&H, fees. Returns and MDD recomputed from daily `equity` and `close` columns in frozen CSVs.

| Ticker | Regime | Days | B&H | Agent (net) | Gross | Fee drag | α vs B&H | B&H MDD | Agent MDD | Fees ($) | B/H/S |
|--------|--------|------|-----|-------------|-------|----------|----------|---------|-----------|----------|-------|
| RELIANCE | Bear | 111 | −17.43% | −7.54% | −6.53% | 1.01 pp | +9.89 pp | 21.0% | 5.11% | 1,010 | 7/28/76 |
| RELIANCE | Bull | 108 | +15.09% | +5.56% | +6.19% | 0.64 pp | −9.53 pp | 11.0% | 2.80% | 635 | 9/25/74 |
| TCS | Bear | 88 | −20.42% | −4.83% | −2.92% | 1.91 pp | +15.59 pp | 23.9% | 6.78% | 1,910 | 12/24/52 |
| TCS | Bull | 67 | +21.86% | +19.61% | +21.80% | 2.20 pp | −2.25 pp | 5.5% | 1.65% | 2,198 | 13/14/40 |

**Table 2.** Secondary risk-adjusted metrics (post-hoc on frozen daily equity; excess Sharpe uses **6.5% p.a.** risk-free rate[^sharpe252]).

| Ticker | Regime | Excess Sharpe (agent) | Excess Sharpe (B&H) | Sortino | Calmar |
|--------|--------|----------------------|---------------------|---------|--------|
| RELIANCE | Bear | −4.27 | −2.51 | −3.10 | −0.96 |
| RELIANCE | Bull | +0.74 | +1.25 | +3.67 | +1.94 |
| TCS | Bear | −2.69 | −3.13 | −2.25 | −0.71 |
| TCS | Bull | +3.86 | +3.27 | +24.22 | +11.88 |

Short windows and discrete daily rebalancing make risk ratios **noisy**; we interpret Table 2 alongside Table 1, not in isolation. RELIANCE bull is positive on total return (+5.6%) with positive excess Sharpe (+0.74) but lags B&H on alpha (−9.53 pp).

**Cross-ticker patterns (observed in these windows).**

- **Bear (2/2):** agent **loses less** than B&H on total return and shows **markedly lower MDD** (e.g., RELIANCE bear: 5.1% vs 21.0%). Both runs are **SELL-heavy**, consistent with reduced long exposure during drawdowns.
- **Bull (mixed):** TCS agent **nearly tracks** B&H (+19.6% vs +21.9%, α −2.25 pp); RELIANCE agent **lags** (+5.6% vs +15.1%, α −9.53 pp) with 74 SELL vs 9 BUY days.

**Table 4.** Selected outlook / stance shares (% of trading days). Full pivot in notebook.

| Ticker | Regime | market bullish | market bearish | bull stance buy | bear stance sell |
|--------|--------|----------------|----------------|-----------------|------------------|
| RELIANCE | Bear | 10.8 | 31.5 | 100.0 | 88.3 |
| RELIANCE | Bull | 24.1 | 19.4 | 94.4 | 77.8 |
| TCS | Bear | 22.7 | 33.0 | 71.6 | 53.4 |
| TCS | Bull | 46.3 | 14.9 | 64.2 | 44.8 |

Internal **bull researcher** stances can remain buy-leaning while **final signals** stay defensive—downstream trader and risk stages drive executable actions.

### 4.5 Transaction-cost breakeven and architectural boundaries

**Fee drag vs alpha.** Fee drag is modest (0.6–2.2 pp of initial capital; Table 1). It does **not** explain RELIANCE bull under-participation: the **−9.53 pp alpha gap** dominates **0.64 pp** fee drag. In bear windows, defensive positioning yields **positive alpha** (+9.89 pp REL, +15.59 pp TCS) despite similar fee levels—suggesting **exposure management**, not costs, drives regime-split outcomes.

**Simplified breakeven spread.** Let \(K\) be non-HOLD signal days and \(F\) total fees. A coarse **fee-and-turnover breakeven** is the average daily edge required to justify rebalancing: \(F / (V_0 \cdot K)\). For RELIANCE bull (\(K=83\) actionable days, \(F=\$635\)), this is ≈**7.7 bps/day**—far below the **~88 bps/day** implied alpha shortfall (\(9.53\%/108\) days). The binding constraint is **SELL-heavy coordination** (74 SELL days), not delivery fees alone.

**Architectural boundary (hypothesis).** Multi-stage debate → trader → risk can **compress drawdown** in bear windows but **cap rally participation** in bull windows when final policy stays defensive despite buy-leaning researcher stances (Table 4). RELIANCE bull exemplifies this boundary; TCS bull shows the same stack can **nearly track** B&H when signal balance is less skewed (13 BUY, 40 SELL). We frame this as **regime × issuer interaction under one architecture**, not a universal win/loss verdict.

We do **not** estimate latency-driven slippage (full **Coordination Breakeven Spread** per Nguyen and Pham, 2026); that remains future work alongside StockSim-class order-level simulation (Papadakis et al., 2025).

### 4.6 Figures

```bash
MPLCONFIGDIR=.mpl_cache .venv/bin/python scripts/generate_paper_figures.py
```

- **`fig_regime_equity_grid`** — 2×2 agent vs B&H panels  
- **`fig_regime_returns_by_ticker`** — total return bars (four runs)  
- **`fig_regime_signals_by_ticker`** — BUY/HOLD/SELL counts  
- **`fig_regime_outlook_bullish`** — bullish analyst-outlook share heatmap  

---

## 5. Conclusion

We presented **Hindsight 20/20**, a reproducible point-in-time LangGraph stack with structured outputs, optional anonymization, and fee-aware backtesting, plus a **scoped four-window case study** on **RELIANCE.NS** and **TCS.NS**. In the **observed bear windows**, the full pipeline shows **lower loss and drawdown** than buy-and-hold; **bull-window outcomes are heterogeneous**, consistent with an architectural trade-off between defensive coordination and rally participation.

**Limitations and future work.**

- **Inferential scope:** N=1 per regime window; no multi-seed variance; two tickers—not an index universe.
- **Calendars:** Per-ticker windows are not synchronous; no shared macro calendar claim.
- **Model and ablations:** Single LLM (`qwen/qwen3.5-flash-02-23`); anonymization on but not ablated; `a1`–`a3` presets not evaluated in §4.
- **Metrics:** Short windows; risk ratios are secondary; no latency/slippage CBS; Infosys windows in `regime-timeranges` planned but not run.
- **Future empirical work (out of scope here):** multi-seed trials, broader PIT universes, anonymization ablations, and full CBS with measured agent latency.

Regimes are **exogenous labels**, not agent predictions. **Not claimed:** SOTA returns; regime forecasting; statistical generalization beyond the four frozen windows.

---

## Contributions

1. **Reproducible backtest harness and frozen artifacts** — fee-aware paper ledger, schedule CSVs, replication scripts (S5 / M6).  
2. **Point-in-time data policy and optional anonymization** — simulation end date at vendor routing; deterministic ticker aliases (S4 / M4–M5).  
3. **Structured stage outputs** — Pydantic-constrained artifacts for audit and traceability (S3 / M3).  
4. **Multi-agent decision graph** with tool-bound analyst decomposition (S1 / M1).  
5. **Honest regime-conditioned case study** — four pre-specified windows, documented limits, architectural-boundary interpretation (S2 / E1).

**Not claimed:** SOTA returns; regime prediction; multi-seed benchmarks; ablation studies in §4.

---

## Acknowledgements

The agent graph implementation builds on **TradingAgents** (Xiao et al., 2024; Tauric Research, Apache License 2.0). We thank the authors for open-sourcing the framework.

---

## References

Badica, C., Badica, A., Ganzha, M., Ivanović, M., Paprzycki, M., Selişteanu, D. and Wrona, Z., 2025. Contemporary Agent Technology: LLM-Driven Advancements vs Classic Multi-Agent Systems. *arXiv preprint* arXiv:2509.02515 [cs.MA]. https://arxiv.org/abs/2509.02515

Bailey, D.H., Borwein, J.M., López de Prado, M. and Zhu, Q.J., 2014. Pseudo-Mathematics and Financial Charlatanism: The Effects of Backtest Overfitting on Out-of-Sample Performance. *Notices of the American Mathematical Society*, 61(5), pp.458–471. https://doi.org/10.1090/noti1105

Dewansh, S., 2026. Policy Convergence and Explainable Stability in Orchestrated Multi-Agent LLM Trading Frameworks. *International Journal of Advanced Engineering and Management Science*, 12(2), pp.058–064. https://doi.org/10.22161/ijaems.122.8

Jeon, J. and Lee, H., 2026. Can Blindfolded LLMs Still Trade? An Anonymization-First Framework for Portfolio Optimization. *arXiv preprint* arXiv:2603.17692 [cs.LG]. https://arxiv.org/abs/2603.17692

Li, X., Zeng, Y., Xing, X., Xu, J. and Xu, X., 2025. QuantAgents: Towards Multi-agent Financial System via Simulated Trading. In *Findings of the Association for Computational Linguistics: EMNLP 2025*, pp.17438–17464, Suzhou, China. https://doi.org/10.18653/v1/2025.findings-emnlp.945

Miyazaki, K., Kawahara, T., Roberts, S. and Zohren, S., 2026. Toward Expert Investment Teams: A Multi-Agent LLM System with Fine-Grained Trading Tasks. *arXiv preprint* arXiv:2602.23330 [cs.AI]. https://arxiv.org/abs/2602.23330

Nguyen, P. and Pham, T., 2026. Toward Reliable Evaluation of LLM-Based Financial Multi-Agent Systems: Taxonomy, Coordination Primacy, and Cost Awareness. *arXiv preprint* arXiv:2603.27539 [cs.MA]. https://arxiv.org/abs/2603.27539

Papadakis, C., Filandrianos, G., Dimitriou, A., Lymperaiou, M., Thomas, K. and Stamou, G., 2025. StockSim: A Dual-Mode Order-Level Simulator for Evaluating Multi-Agent LLMs in Financial Markets. *arXiv preprint* arXiv:2507.09255 [cs.CE]. https://arxiv.org/abs/2507.09255

Qian, L., Peng, X., Wang, Y., Zhang, V.J., He, H., Li, Z., Smith, H., Han, Y., He, Y., Li, H., Cao, Y., Yu, Y., Lopez-Lira, A., Lu, P., Nie, J.-Y., Xiong, G., Huang, J. and Ananiadou, S., 2026. When Agents Trade: Live Multi-Market Trading Arena for LLM Agents. In *Proceedings of the ACM Web Conference 2026*. https://doi.org/10.1145/3774904.3792821

Xiao, Y., Sun, E., Luo, D. and Wang, W., 2024. TradingAgents: Multi-Agents LLM Financial Trading Framework. *arXiv preprint* arXiv:2412.20138 [q-fin.TR]. https://arxiv.org/abs/2412.20138

Yang, H., Liu, X.-Y. and Wang, C.D., 2023. FinGPT: Open-Source Financial Large Language Models. *arXiv preprint* arXiv:2306.06031 [q-fin.ST]. https://arxiv.org/abs/2306.06031

Yu, Y., Li, H., Chen, Z., Jiang, Y., Li, Y., Zhang, D., Liu, R., Suchow, J.W. and Khashanah, K., 2023. FinMem: A Performance-Enhanced LLM Trading Agent with Layered Memory and Character Design. *arXiv preprint* arXiv:2311.13743 [q-fin.CP]. https://arxiv.org/abs/2311.13743

Zhao, T., Lyu, J., Jones, S., Garber, H., Pasquali, S. and Mehta, D., 2025. AlphaAgents: Large Language Model based Multi-Agents for Equity Portfolio Constructions. *arXiv preprint* arXiv:2508.11152 [q-fin.ST]. https://arxiv.org/abs/2508.11152

---

## Changelog

| Date | Change |
|------|--------|
| 2026-05-29 | Expanded references and Related Work contrasts (Nguyen and Pham, Jeon and Lee, Bailey et al., Miyazaki et al., Li et al., Zhao et al., Papadakis et al., Qian et al., Dewansh, Bădică et al.). |
| 2026-05-29 | Multi-ticker Frozen E1: TCS + completed REL bull through 2025-06-03. |
