# Manuscript (draft — export to PDF / LaTeX)

**Purpose:** Submission-facing prose only. Scope and checklist live in [paper-roadmap.md](paper-roadmap.md). Claims must match **`.cursor/memory.md`** and [claim-evidence-map.md](claim-evidence-map.md).

**Last updated:** 2026-05-28.

**PDF:** `pandoc docs/paper/manuscript.md -o paper-draft.pdf --pdf-engine=tectonic` (requires LaTeX engine). IOS package: `./docs/paper/submission/build_ios_package.sh`.

---

## Working title

*Point-in-Time Multi-Agent LLM Trading: A Reproducible LangGraph Stack with Regime-Conditioned Evaluation and Fair Backtesting*

---

## Abstract

Large language models are increasingly used in financial decision pipelines, yet published agent stacks are often hard to reproduce, weakly specified at the tool-and-data boundary, and rarely evaluated under distinct **market conditions** on historical “as of” dates. We present **Hindsight 20/20**, an open-source **LangGraph** implementation for single-asset trading research that composes specialist analysts, investment and risk debate, and structured **Pydantic** stage outputs. Market retrieval enforces a **simulation end date** for point-in-time access, with optional **ticker anonymization**. A **paper backtest** replays daily signals with configurable costs. We evaluate the **full** multi-agent pipeline on **RELIANCE.NS** in two **exogenous** calendar windows—a **bear regime** (underlying return −17.4%, Aug 2024–Jan 2025) and a **bull regime** (+19.3%, Jan–May 2025)—each from fresh paper capital. The agent loses less than buy-and-hold in the bear window (−7.5% vs −17.4%) but captures less of the rally in the bull window (+8.7% vs +19.3%), consistent with a defensive signal profile. Scripts and frozen CSV artifacts reproduce tables and figures. **Langfuse**-compatible tracing supports debugging, not a standalone empirical claim.

*(IOS submission: [`docs/paper/submission/`](submission/) — run `build_ios_package.sh`.)*

---

## 1. Introduction

Researchers are experimenting with large language models (LLMs) as planners, analysts, and debaters inside trading workflows. A single-asset, day-ahead setting is a natural testbed: the model must interpret noisy context, call tools, and emit a discrete action checkable against realized prices. Yet research-grade stacks remain brittle—tool wiring, data routing, and temporal constraints are often implicit, and evaluations rarely separate **how the same stack behaves when the underlying trend differs**.

We target **historical, point-in-time** use: on each trade date the pipeline may only consume information available on or before that date. We also care about **traceability**: stage artifacts should be inspectable without scraping unstructured blobs.

This paper presents **Hindsight 20/20**, an open **LangGraph** implementation focused on *reproducibility and auditable evaluation* rather than claiming state-of-the-art returns. The same graph drives UI/CLI and scripted backtests. **Structured outputs** (Pydantic with fallbacks) validate intermediate decisions. Optional **anonymization** limits direct ticker exposure in model-visible strings. A **paper backtest** replays signals through a fee-aware ledger.

**Empirical focus.** We run the **full** pipeline (`PAPER_ABLATION=full`: all analysts, investment debate, risk phase) on one Indian listing (**RELIANCE.NS**) in two **independent** backtests over calendar windows labeled **bear** and **bull** from exogenous underlying returns (§4.1). Each run starts from **$100,000** paper cash; we compare agent equity paths to **buy-and-hold** on the same window.

**Structure.** §2 surveys related work. §3 describes the system. §4 reports the regime protocol and frozen results. §5 concludes. **Contributions** are listed at the end.

---

## 2. Related Work

*Starter BibTeX keys: [bib-seed.bib](bib-seed.bib) (`xiao2024tradingagents`, `yu2023finmem`, `yang2023fingpt`).*

**LLM agents for trading and finance.** Recent frameworks orchestrate specialist roles toward trading outputs (Xiao et al., 2024; Yu et al., 2023; Yang et al., 2023). Our work is complementary: we foreground **reproducible systems engineering**—one LangGraph codepath, schema-constrained outputs, temporal controls, and a scriptable backtest tied to **concrete CSV artifacts**.

**Point-in-time data, leakage, and memorization.** Tool-augmented agents can mis-specify temporal semantics across vendors; strong models may exploit ticker cues. We treat a **simulation end date**, centralized vendor routing, and **optional anonymization** as first-class requirements.

**Robustness across market conditions.** Agent behavior may differ when trends, volatility, or news tone shift. Prior stacks rarely document **regime-split** backtests on the **same** implementation with frozen protocols. We contribute a small, fully specified bear/bull comparison on one ticker—not regime *prediction*, but *evaluation* under exogenous labels.

**Execution realism.** We link model decisions to **fees, ledger state, and mark-to-market** via a paper-ledger backtest (`zerodha_delivery` in our runs), without claiming limit-order-book fidelity.

**Positioning.** Hindsight 20/20 does not introduce a new benchmark winner. It contributes an open narrative: multi-agent LangGraph orchestration, structured outputs, temporal and anonymization controls, and **regime-conditioned** evaluation from stored runs.

---

## 3. Method / System

File-level pointers: **`.cursor/memory.md`**.

### 3.1 Architecture

**`TradingAgentsGraph`** wires LangGraph nodes—specialist analysts, optional **Bull Researcher** / **Bear Researcher** investment debate (internal debate roles, distinct from §4 market regimes), trader synthesis, optional risk debate and judge, and signal extraction. The same graph backs **`run_backtest_mvp`**.

### 3.2 Agents, tools, and data routing

Analyst modules consume tools on **`tradingagents.agents.utils.agent_utils`**, backed by **`tradingagents/dataflows/`** vendors and **`set_config`**.

### 3.3 Structured stage outputs

Pydantic models in **`tradingagents/schemas/`** with **`invoke_fallback`** merge validated JSON into graph state (**S3** / **M3**).

### 3.4 Point-in-time policy

**`effective_simulation_end_date_str`** clamps vendor reads to the simulation date (**M4**).

### 3.5 Optional ticker anonymization

**`TickerMapper`** substitutes opaque identifiers in prompts and tool I/O where configured (**M5**). Frozen E1 runs used anonymization (`STOCK_4264` in logs).

### 3.6 Pipeline configuration

§4 uses **`PAPER_ABLATION=full`** (default in **`default_config.py`**): all four analysts, investment debate on, risk phase on. The repo also ships **`a1`–`a3`** presets via **`tradingagents/paper_ablation.py`** for internal sweeps; they are **not** part of the empirical claims here (**M2**).

### 3.7 Paper backtest harness

**`run_backtest_mvp`** calls **`graph.propagate`** per day, maps output to **`BUY` / `SELL` / `HOLD`**, and fills through **`PaperLedger`** with configurable **`cost_model`** (**M6**). **`scripts/backtest_mvp.py --dates-csv`** writes wide schedule CSVs (signals, equity, per-stage outlook columns).

### 3.8 Observability (non-empirical)

Optional Langfuse correlation metadata for debugging; not used as evidence in §4.

---

## 4. Experiments

### 4.1 Goals, scope, and regime definition

We evaluate the **full** pipeline on **one ticker (`RELIANCE.NS`)** under two **exogenous market regimes**—calendar windows chosen before backtests and labeled from the **underlying adjusted close** over each window (independent of agent signals or debate-role names).

| Regime label | Assignment rule (underlying B&H over processed window) |
|--------------|--------------------------------------------------------|
| **Bear** | Total return **≤ −10%** |
| **Bull** | Total return **≥ +10%** |

Each regime is a **separate backtest** with **$100,000** initial paper cash (no carry-over). We compare **agent total return** to **buy-and-hold** on the same window. We do **not** claim universality, regime forecasting, or optimality.

**Frozen artifacts:** [claim-evidence-map.md](claim-evidence-map.md) (**Frozen E1**).

### 4.2 Protocol

**Bear window.** Schedule CSV **`results/dates-REL-aug-2024-jan-2025-bear-dates.csv`**, processed **2024-08-01** through **2025-01-03** (111 trading days), via:

```bash
python scripts/backtest_mvp.py --ticker RELIANCE.NS \
  --dates-csv results/dates-REL-aug-2024-jan-2025-bear-dates.csv
```

**Bull window.** **`results/dates-REL-jan-2025-june-2025-bull-dates.csv`**, processed **2025-01-01** through **2025-05-16** (94 trading days; schedule targets June 2025 but the frozen artifact stops at the last successful day before API rate limits). Same driver command with the bull CSV.

**Shared settings:** `PAPER_ABLATION=full`; **`initial_cash=100,000`**; **`cost_model=zerodha_delivery`**, **`slippage_bps=0`**; ticker anonymization enabled; LLM **`qwen/qwen3.5-flash-02-23`** (OpenRouter). Logs under **`eval_results/dates-REL-*-dates.log`**.

**Analysis:** **`scripts/backtest_regime_analysis.ipynb`** (Tables 1–2); figures via **`scripts/generate_paper_figures.py`**.

### 4.3 Results

**Table 1.** Agent vs buy-and-hold by regime (frozen CSVs, $100,000 start).

| Regime | Window (processed) | Days | B&H return | Agent return | Ending equity | Max DD | Sharpe | Signals (B/H/S) | Fees ($) |
|--------|-------------------|------|------------|--------------|---------------|--------|--------|-------------------|----------|
| Bear | 2024-08-01 .. 2025-01-03 | 111 | −17.43% | −7.54% | $92,459.38 | 5.11% | −3.12 | 7 / 28 / 76 | 1,010.32 |
| Bull | 2025-01-01 .. 2025-05-16 | 94 | +19.25% | +8.68% | $108,675.02 | 0.47% | +2.62 | 6 / 20 / 68 | 613.69 |

In the **bear** window, the agent **outperforms buy-and-hold** on total return while remaining net short of peak capital—consistent with predominantly **SELL** signals (76 of 111 days) that reduce drawdown exposure. In the **bull** window, the agent **underperforms buy-and-hold** despite positive absolute return—only **six BUY** days versus **68 SELL**, so the stack participates partially in the rally. These patterns illustrate **regime sensitivity** of a defensive policy; they are **not** evidence of general superiority.

**Table 2.** Selected stage outlook and debate stance shares (% of trading days). Full breakdown in **`backtest_regime_analysis.ipynb`**.

| Regime | Field | bullish | bearish | mixed | neutral | buy | sell | hold |
|--------|-------|---------|---------|-------|---------|-----|------|------|
| Bear | market_outlook | 10.8 | 31.5 | 48.6 | 3.6 | — | — | — |
| Bear | bull_implied_stance | — | — | — | — | 100.0 | — | — |
| Bear | bear_implied_stance | — | — | — | — | — | 88.3 | 10.8 |
| Bull | market_outlook | 21.3 | 21.3 | 46.8 | 3.2 | — | — | — |
| Bull | bull_implied_stance | — | — | — | — | 97.9 | — | 1.1 |
| Bull | bear_implied_stance | — | — | — | — | — | 85.1 | 12.8 |

The **bull researcher** stance is uniformly **buy** in the bear window while **final signals** remain sell-heavy (Table 1)—downstream aggregation and risk phases, not a single debate node, drive executable actions.

### 4.4 Figures

```bash
MPLCONFIGDIR=.mpl_cache .venv/bin/python scripts/generate_paper_figures.py
```

Writes **`docs/paper/figures/`**:

- **`fig_regime_equity`** — agent vs buy-and-hold per window  
- **`fig_regime_returns`** — bar chart of total returns  
- **`fig_regime_signals`** — BUY/HOLD/SELL counts  
- **`fig_regime_outlook_bullish`** — share of bullish analyst outlook days  

A conceptual LangGraph DAG from **`GraphSetup`** remains optional venue artwork.

---

## 5. Conclusion

We presented **Hindsight 20/20**, an open LangGraph stack with structured outputs, point-in-time data routing, optional anonymization, and a fee-aware paper backtest. On **RELIANCE.NS**, the **full** pipeline under **exogenous bear and bull windows** shows asymmetric behavior: relative protection in the bear regime and partial participation in the bull regime, with transparent CSV artifacts and notebooks for reproduction.

**Limitations.** One ticker; two hand-selected windows; **bull run truncated at 2025-05-16**; single LLM and vendor configuration; anonymization enabled; no microstructure simulation. Regime labels are **not** produced by the agent. Future work: broader universes, model sweeps, and features in **`ROADMAP.md`** once implemented.

---

## Contributions

Maps to **S1–S5** in [STORY_LOCK.md](STORY_LOCK.md) and [claim-evidence-map.md](claim-evidence-map.md).

1. **Multi-agent decision graph** (S1 / M1): LangGraph pipeline with analysts, debate, and risk stages on one codepath.

2. **Regime-conditioned evaluation** (S2 / E1): Independent backtests under exogenous bear and bull calendar windows with agent vs buy-and-hold comparison from frozen CSVs.

3. **Structured stage outputs** (S3 / M3): Pydantic-constrained LLM artifacts in graph state.

4. **Point-in-time policy and optional anonymization** (S4 / M4–M5): Simulation-date cap and vendor routing; anonymized ticker in Frozen E1 runs.

5. **Backtest harness and analysis artifacts** (S5 / M6): Fee-aware ledger, schedule CSVs, **`backtest_regime_analysis.ipynb`**, and **`generate_paper_figures.py`**.

**Not claimed:** state-of-the-art returns; regime prediction; ablation-depth comparisons in §4.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-05-28 | Regime experiments replace ablation study; §4 and contributions rewritten. |
