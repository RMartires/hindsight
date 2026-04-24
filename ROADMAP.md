# TradingAgents — Implementation Roadmap

> Gap analysis against the **Single-Stock Multi-Agent Trading System** paper architecture.
> **Last synced to the repo implementation:** April 24, 2026 (earlier “April 2026” audit still applies to most sections).

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Already implemented |
| 🔶 | Partially implemented — needs extension |
| ❌ | Not implemented — greenfield work |

---

## Module 1 · Infrastructure & Orchestration

### 1.1 JSON Schema Enforcer 🔶
**What it is:** Force all LLM outputs that feed downstream code to conform to a strict JSON schema, preventing parsing failures during automated signal extraction and feature engineering.

**Current state (partial):** `tradingagents/schemas/outputs.py` defines Pydantic models used in the pipeline: `AnalystReport`, `BullBearArgument`, `RiskAnalystArgument`, `InvestmentPlanJudgment`, `TradeProposal`, `RiskAssessment`. `llm_clients/invoke_fallback.py` binds LangChain `.with_structured_output(...)` (`json_schema` / `json_mode`) with deep→quick model fallback, parse-failure logging, and (for several nodes) fallback to plain text if structured invoke fails. The four analysts, bull/bear researchers, research manager, trader, three risk debators, and risk manager write structured JSON into `AgentState` via `*_structured` keys (values are **JSON strings** for serialization). Prose drafts still precede structured extraction on many paths. `validators.py` still only validates LLM **model names** in config — unrelated to output schemas.

**What to build (remaining):**
- [ ] Add a structured **debate transcript** model (e.g. per-round `DebateRound` or equivalent) if multi-round debate is expanded (see §2.5)
- [ ] Optional: persist validated outputs as **typed** objects in `AgentState` instead of only JSON strings (trade-offs with LangGraph checkpointing)
- [ ] Optional: explicit **re-prompt on schema violation** up to N attempts (today: structured invoke + deep LLM fallback + plain-text fallback)
- [ ] Audit for any node that still feeds downstream logic with prose-only output

---

### 1.2 Rolling Context Window Manager 🔶
**What it is:** A module that maintains a fixed-length sequence of the last 7–10 days of prices and agent decisions in the prompt, giving the LLM temporal context without ballooning token usage.

**Current state:** `llm_max_input_tokens` trims analyst **message lists** (newest-first, ~4 chars/token heuristic). Researchers, trader, and risk debators build giant f-string prompts with no trimming. `FinancialSituationMemory` is BM25 retrieval of past text situations — not a structured rolling buffer of numeric observations.

**What to build:**
- [ ] Extend trimming to **all** agent nodes (researchers, trader, risk debators), not just the four analysts
- [ ] Build a `RollingObservationBuffer` that stores `(date, OHLCV, signal)` tuples for the last N days
- [ ] Serialize the buffer as a compact table and inject it into every agent's system prompt
- [ ] Make the window size configurable (default: 7 days) in `DEFAULT_CONFIG`
- [ ] Add proper token counting (tiktoken / provider-specific tokenizer) to replace the 4-chars heuristic

---

## Module 2 · Agentic Intelligence Layer

### 2.1 Technical Analyst 🔶
**What it is:** An agent that interprets **normalized** technical indicators (MACD, RSI, KDJ) to detect trading patterns.

**Current state (partial):** `market_analyst.py` uses `get_indicators` and injects the **Tier-1** catalog from `tradingagents/dataflows/indicator_library.py` via `format_tier1_indicator_list_for_prompt()` (single source of truth for tool names + LLM copy). Vendors `y_finance.py`, `kite_indicator.py`, and `alpha_vantage_indicator.py` validate indicators with `validate_tier1_indicator` / use `tier1_indicator_descriptions()`. Indicators are still **raw stockstats values** (not min-max / z-score **normalized**). **KDJ is not in the Tier-1 catalog yet**.

**What to build:**
- [ ] Add **KDJ** to `indicator_library.py` (Tier-1) and ensure stockstats column names are wired; keep vendor validation consistent
- [ ] Add a **normalization layer** in `stockstats_utils.py` (or post-process in the indicator path) that min-max scales or z-scores each indicator over its rolling window before tool/prompt return
- [ ] Update the market analyst system prompt to reflect normalized value ranges (0–1 or z-score) once normalization exists

---

### 2.2 Quantitative Analyst ❌
**What it is:** A dedicated agent focused on professional accounting sub-tasks — inventory turnover period, DuPont decomposition, ROE/ROA trend analysis, and other quant finance ratios.

**Current state:** No dedicated quant agent. The fundamentals analyst fetches ROE/ROA as raw `yfinance` fields but does no ratio decomposition or trend analysis.

**What to build:**
- [ ] Create `tradingagents/agents/analysts/quant_analyst.py`
- [ ] Define tools: `get_roe_roa_trend`, `get_inventory_turnover`, `get_dupont_decomposition`, `get_liquidity_ratios`
- [ ] Implement these tools in `tradingagents/dataflows/` using income statement + balance sheet data
- [ ] Wire the quant analyst into `graph/setup.py` as a fifth selectable analyst
- [ ] Add `"quant"` to the `selected_analysts` list in `DEFAULT_CONFIG`

---

### 2.3 News & Sentiment Analyst 🔶
**What it is:** An agent that performs fine-grained semantic nuance analysis of filtered, anonymized news headlines.

**Current state:** `social_media_analyst.py` + `news_analyst.py` exist. Both pass raw headlines directly to the LLM. Semantic nuance comes purely from the model's reading — no sentiment scoring, no filtering pipeline, no anonymization.

**What to build:**
- [ ] Add a **pre-filter step** that scores headlines by relevance to the ticker before they enter the agent prompt
- [ ] Integrate the anonymization scrubber (see Module 3.2) into the news pipeline
- [ ] Optionally add a lightweight sentiment score (e.g. FinBERT embedding) as a structured field alongside each headline

---

### 2.4 Macro Analyst 🔶
**What it is:** A dedicated agent that reads structured macro time series — interest rates, inflation, GDP — rather than inferring macro context from news articles.

**Current state:** `news_analyst.py` mentions macroeconomics and uses `get_global_news`, but there is no dedicated macro agent and no structured time-series tools for rates/inflation/GDP.

**What to build:**
- [ ] Create `tradingagents/agents/analysts/macro_analyst.py`
- [ ] Add data tools: `get_interest_rates`, `get_inflation_data`, `get_gdp_data` backed by FRED API (or yfinance macro tickers like `^TNX`, `^FVX`)
- [ ] Wire into `graph/setup.py` as a selectable analyst
- [ ] Add `"macro"` to `selected_analysts` options in `DEFAULT_CONFIG`

---

### 2.5 Adversarial Debate Logic 🔶
**What it is:** A Debate Facilitator that manages n-rounds of structured back-and-forth between Bull and Bear researchers before reaching consensus.

**Current state:** Bull ↔ Bear alternation exists, gated by `max_debate_rounds` (default = 1 round = one Bull + one Bear turn). `Research Manager` acts as a post-debate summarizer/judge, not a live moderator.

**What to build:**
- [ ] Promote `Research Manager` to an **active facilitator** role that poses a targeted rebuttal question to each side after each round (not just summarizes at the end)
- [ ] Add a **structured debate transcript** object (list of `{speaker, argument, evidence_refs}`) stored in `AgentState`
- [ ] Make it easy to run 3–5 debate rounds via config without hitting context limits (tie into the rolling context window)

---

### 2.6 CRO Veto Gate 🔶
**What it is:** A Chief Risk Officer class that vetoes or downsizes a trade proposal based on **programmatic** checks of portfolio beta, liquidity ratios, and sector exposure — not just LLM text judgment.

**Current state:** Three risk debators (Aggressive/Conservative/Neutral) + a Risk Judge exist. The Risk Judge's final `BUY/SELL/HOLD` is a pure LLM text decision with no hard programmatic thresholds or veto logic.

**What to build:**
- [ ] Add a `CROVetoGate` class in `tradingagents/agents/risk_mgmt/cro_veto.py`
- [ ] Implement hard-coded checks (configurable thresholds):
  - Portfolio Beta > 1.5 → reduce position size / veto
  - Bid-ask spread / volume liquidity ratio above threshold → veto MARKET order
  - Sector concentration > X% → flag
- [ ] Run the veto gate **after** the Risk Judge, before writing `final_trade_decision`
- [ ] If vetoed, write reason to `AgentState` and emit `HOLD` with explanation

---

## Module 3 · Anonymization & Data Engineering

### 3.1 Ticker Mapping Engine ❌
**What it is:** A dictionary-based module that replaces real tickers with synthetic IDs (e.g. `AAPL → STOCK_0026`) in all agent prompts to mitigate LLM memorization bias.

**Current state:** Tickers flow through verbatim in all prompts and tool outputs. The only symbol mapping is Kite's instrument token resolution for broker API calls.

**What to build:**
- [ ] Create `tradingagents/anonymization/ticker_map.py`
- [ ] Generate a deterministic, reversible mapping (real ticker → `STOCK_XXXX`)
- [ ] Apply the mapping in `Propagator.create_initial_state` before the ticker enters `AgentState`
- [ ] Strip real ticker from all tool output strings (OHLCV column headers, `yfinance` metadata fields)
- [ ] Reverse-map only in the final result/logging layer

---

### 3.2 Proper Noun Scrubber ❌
**What it is:** A text processing step that replaces company names, executive names, and product names (e.g. "Elon Musk" → "CEO of AUTO_COMPANY_0003") in news headlines before they reach an LLM.

**Current state:** Headlines go to the LLM verbatim. No entity scrubbing, no Knowledge Graph integration.

**What to build:**
- [ ] Create `tradingagents/anonymization/noun_scrubber.py`
- [ ] Integrate [Google Knowledge Graph Search API](https://developers.google.com/knowledge-graph) (or spaCy NER as a free alternative) to detect named entities in headline text
- [ ] Build a replacement map: person names → generic role descriptions, product names → generic category labels
- [ ] Apply scrubber to all `get_news` and `get_global_news` tool outputs before they are returned to agent prompts
- [ ] Add `GOOGLE_KG_API_KEY` to `.env.example`

---

### 3.3 60-Indicator Library 🔶
**What it is:** Pre-calculate 60 standard technical indicators from raw OHLCV data to provide fine-grained inputs for the Technical Agent.

**Current state (partial):** `tradingagents/dataflows/indicator_library.py` exists. **v1** ships a **Tier-1** catalog (~**13** logical `indicator_id`s: trend + momentum + volatility + volume) with `IndicatorSpec`, `validate_tier1_indicator`, `compute_indicators(ohlcv, indicator_ids)`, and `format_tier1_indicator_list_for_prompt()`. Vendors and `market_analyst` consume this module (no duplicate hardcoded “best params” list per vendor). Tests: `tradingagents/tests/test_indicator_library.py`. This is the **infrastructure** for a larger library; the **60-indicator** breadth below is not implemented yet.

**What to build (remaining):**
- [ ] Grow the catalog toward **60** indicators across categories (see original paper scope):
  - **Trend** (SMA-5/10/20/50/100/200, EMA-5/10/20/50, WMA, DEMA, TEMA, HMA, KAMA)
  - **Momentum** (RSI-14, MACD, Signal, Histogram, ROC, MOM, CCI, Williams %R, KDJ, Stochastic, StochRSI)
  - **Volatility** (ATR, Bollinger Bands, Keltner Channel, Donchian Channel, Historical Vol)
  - **Volume** (OBV, VWAP, VWMA, MFI, CMF, AD, Force Index, VROC)
  - **Trend strength** (ADX, +DI, -DI, Aroon Up/Down, PSAR)
  - **Oscillators** (DPO, TRIX, UO, PPO, Detrended Price)
- [ ] (Optional) Tiering: keep **Tier-1** small for LLM + validation; add Tier-2+ ids and validation rules as the catalog grows
- [ ] Update the market analyst prompt and vendor docs to reflect the **expanded** catalog when added

---

## Module 4 · High-Fidelity Simulation Engine

### 4.1 Limit Order Book (LOB) Simulator ❌
**What it is:** An order-matching engine that processes MARKET, LIMIT, and STOP orders with price-time priority, simulating realistic fills.

**Current state:** `PaperLedger` is a simple cash/shares book that executes BUY/SELL at the day's raw close price. No order types, no partial fills, no LOB mechanics.

**What to build:**
- [ ] Create `tradingagents/simulation/order_book.py` with a `LimitOrderBook` class
- [ ] Implement order types: `MarketOrder`, `LimitOrder`, `StopOrder`
- [ ] Match against the OHLCV-reconstructed order flow using price-time priority
- [ ] Model partial fills (volume-limited) and price impact (linear or square-root model)
- [ ] Replace `PaperLedger.apply_signal` with `OrderBook.submit(order)` in `backtest/runner.py`
- [ ] Keep `PaperLedger` as a simple fallback mode

---

### 4.2 Temporal Partitioning Controller 🔶
**What it is:** A strict knowledge cutoff that ensures no agent ever sees data beyond the simulation as-of date relative to `trade_date`.

**Current state (partial):** `TradingAgentsGraph.propagate` sets `simulation_data_end` from `trade_date` via `simulation_context.effective_simulation_end_date_str` (default policy: **prior calendar day**). `route_to_vendor` clamps `get_stock_data`, `get_news`, `get_indicators`, and `get_global_news` date args. `stockstats_utils` / `y_finance` bulk downloads use `effective_data_end_date()` instead of wall-clock `today`. yfinance ticker news **excludes articles without a publish date** so undated items cannot bypass the window.

**Backtest EOD / execution (fixed Apr 2026):** Agent tools must stay capped to the prior information date, but **marking portfolio value at the day’s close** must still request that session’s bar. The execution path `fetch_close_for_trade_date` in `tradingagents/backtest/prices.py` passes `eod_for_trade_date=...` into `route_to_vendor`, which uses `simulation_context.clamp_date_range_eod` (effective cap is at least `trade_date+1` calendar day) so a Monday backtest is not forced to only query a non-trading Sunday. Tests: `tradingagents/tests/test_simulation_temporal.py`.

**Kite robustness (partial):** `kite_stock.get_stock_data` retries on `ConnectionResetError` in addition to `requests` connection errors (transient network disconnects to Zerodha).

**What to build:**
- [ ] Extend clamping / `simulation_data_end` to any remaining tool paths that accept dates (e.g. fundamentals if applicable)
- [ ] Add integration tests with mocked vendor responses asserting row dates ≤ cap

---

### 4.3 Transaction Cost Model 🔶
**What it is:** Realistic per-trade costs and net vs gross reporting.

**Current state:** `PaperLedger` supports **`cost_model`**: `flat_bps` (legacy), **`zerodha_delivery`**, **`zerodha_intraday`** via `tradingagents/backtest/zerodha_fees.py` (rates cited from Zerodha charge list). **`slippage_bps`** adds an extra haircut on notional. `summary.json` includes **`gross_total_return`** vs **`total_return`** (net). Env: `BACKTEST_COST_MODEL`, `BACKTEST_SLIPPAGE_BPS`, `KITE_BROKERAGE_BPS` (default bps when `BACKTEST_COST_BPS` unset in `scripts/backtest_mvp.py`).

**What to build:**
- [ ] Optional advanced slippage (e.g. size/volume-based) beyond flat `slippage_bps`

---

## Module 5 · Evaluation & Analytics Suite

### 5.1 Financial Performance Engine 🔶
**What it is:** Standard ROI, Annualized Return, Sharpe/Sortino/Calmar, and Maximum Drawdown calculators.

**Current state:** Implemented in **`tradingagents/backtest/metrics.py`** (`annualized_return`, `sharpe_ratio`, `sortino_ratio`, `calmar_ratio`, `compute_performance_stats`, `gross_total_return`, `buy_and_hold_total_return`). `runner.py` wires metrics into `summary.json` and `dates.csv` analysis columns.

**Stability (fixed):** `annualized_return` returns **`None`** when `1 + total_return < 0` (worse than −100% total return), so Python does not produce a **complex** value from a fractional real exponent; this avoids `TypeError` / non-JSON-serializable `summary.json` in extreme loss paths. Tests: `tradingagents/tests/test_backtest_metrics.py`.

**What to build:**
- [ ] Optional: wire `buy_and_hold_total_return` into `summary.json` when a benchmark series is available

---

### 5.2 Explainable Stability Tracker ❌
**What it is:** A textual comparison tool that measures **Rationale Persistence** — whether the causal story (evidence → analyst signal → researcher stance → trader decision → final order) remains consistent through the pipeline.

**Current state:** Per-date JSON state logs (`full_states_log_<date>.json`) store all intermediate reports, but no tool compares them for consistency. `Reflector` does retrospective narrative memory, not a forward consistency check.

**What to build:**
- [ ] Create `tradingagents/analytics/rationale_tracker.py`
- [ ] Define a `RationaleChain` data class: `{analyst_signals[], researcher_stance, trader_plan, risk_decision, final_signal}`
- [ ] After each run, extract the chain from `AgentState` and use an LLM (or embedding similarity) to score directional consistency between layers
- [ ] Flag "rationale breaks" (e.g. bull analyst → bear researcher → BUY trader) and log them
- [ ] Persist per-date rationale chains to `eval_results/<ticker>/rationale_chains/` for later review

---

### 5.3 CBS Calculator ❌
**What it is:** The **Coordination Breakeven Spread** — a formula that determines whether the alpha generated by multi-agent coordination justifies the latency cost (extra slippage from API call time).

**Current state:** Not implemented. No reference to CBS anywhere in the codebase.

**Formula:**
```
CBS = (avg_latency_seconds × daily_price_volatility_per_second) + cost_bps
```
If `expected_signal_alpha < CBS` → single-agent mode is preferred.

**What to build:**
- [ ] Create `tradingagents/analytics/cbs_calculator.py`
- [ ] Instrument each agent graph run to record per-node LLM call latency (already partially available via Langfuse)
- [ ] Compute intraday price volatility (σ per second) from OHLCV data
- [ ] Implement the CBS formula and compare against back-tested alpha
- [ ] Add CBS to `summary.json` output

---

### 5.4 Visual Diagnostics Dashboard ❌
**What it is:** An interactive frontend to visualize equity curves, candlestick charts with agent decision overlays, and hover-able agent reasoning logs.

**Current state:** No dashboard. Outputs are CSV/JSON files and optional Langfuse traces. `backtrader` is in `pyproject.toml` but never imported.

**What to build:**
- [ ] Create `dashboard/` directory with a Plotly Dash or Streamlit app
- [ ] **Equity curve panel:** line chart of portfolio value over time, with buy/sell markers
- [ ] **Candlestick panel:** OHLCV candles with overlaid technical indicator plots and entry/exit markers
- [ ] **Agent reasoning panel:** hover over any trade marker to see the full analyst → researcher → trader → risk rationale chain for that date
- [ ] **Metric summary panel:** ROI, Annualized Return, Sharpe, MDD, CBS side-by-side
- [ ] Load data from `eval_results/<ticker>/equity.csv` + `full_states_log_*.json`
- [ ] Add `plotly` and `dash` (or `streamlit`) to `pyproject.toml`

---

## Implementation Priority Order

> Suggested sequencing based on dependencies and impact.

| Phase | Items | Rationale |
|-------|-------|-----------|
| **Phase 1 — Foundation** | 4.2 Temporal Cutoff, 4.3 Cost Model, 5.1 Performance Metrics | **Partially done:** EOD price clamp (§4.2), Kite reset retries (§4.2), performance edge cases (§5.1). Remaining: broader tool clamp coverage + tests; optional B&H in `summary` |
| **Phase 2 — Data** | 3.3 Expand indicator catalog, 2.1 (KDJ + norm), 2.4 Macro Analyst | Tier-1 `indicator_library` + vendor wiring exists; still need **scale** to ~60, **KDJ**, and **normalization** |
| **Phase 3 — Agent Quality** | 1.1 JSON Schema (finish gaps), 1.2 Context Window (all nodes), 2.2 Quant Analyst, 2.6 CRO Veto Gate | Finish structured outputs and token management before adding more agents |
| **Phase 4 — Anonymization** | 3.1 Ticker Map, 3.2 Noun Scrubber | Apply to all prompts once agent/data layer is stable |
| **Phase 5 — Simulation** | 4.1 LOB Simulator | High-fidelity execution layer; depends on cost model and temporal cutoff |
| **Phase 6 — Analytics** | 5.2 Rationale Tracker, 5.3 CBS Calculator, 5.4 Dashboard | Evaluation suite; depends on all upstream modules being stable |

---

## File Map (New Files to Create)

### Already present in repo (roadmap items partially landed)

- `tradingagents/dataflows/indicator_library.py` — Tier-1 catalog, `compute_indicators`, prompt helpers (§3.3 partial)
- `tradingagents/tests/test_indicator_library.py` — unit tests for catalog + compute path
- `tradingagents/tests/test_simulation_temporal.py` — `clamp_date_range` / `clamp_date_range_eod` (§4.2)
- `tradingagents/tests/test_backtest_metrics.py` — annualized return edge cases (§5.1)

### Still to create (or expand)

```
tradingagents/
├── anonymization/
│   ├── __init__.py
│   ├── ticker_map.py            # 3.1
│   └── noun_scrubber.py         # 3.2
├── agents/
│   └── analysts/
│       ├── quant_analyst.py     # 2.2
│       └── macro_analyst.py     # 2.4
├── agents/
│   └── risk_mgmt/
│       └── cro_veto.py          # 2.6
├── simulation/
│   ├── __init__.py
│   └── order_book.py            # 4.1
└── analytics/
    ├── __init__.py
    ├── rationale_tracker.py     # 5.2
    └── cbs_calculator.py        # 5.3

dashboard/
├── app.py                       # 5.4
├── panels/
│   ├── equity_curve.py
│   ├── candlestick.py
│   └── reasoning_log.py
└── requirements.txt
```

---

*Last updated: April 24, 2026*
