# Claim–evidence map (memory-aligned)

**Rule:** Each claim below must be supportable from **existing code and artifacts** described in **`.cursor/memory.md`**. Do not add rows that require features listed only in `ROADMAP.md` as not implemented.

**Last updated:** 2026-05-28.

---

## System / method claims (typically no new runs required to *describe*)

| ID | Claim | Evidence |
|----|--------|----------|
| M1 | Multi-agent pipeline with analysts → debate → trader → risk → final decision | `graph/setup.py`, `TradingAgentsGraph`; memory `tradingagents-graph`, `tradingagents-agents` |
| M2 | Four ablation presets change which phases/analysts run *(implementation hook; not evaluated in §4)* | `tradingagents/paper_ablation.py`; memory `config-and-env` |
| M3 | Stages emit structured JSON aligned to Pydantic models | `tradingagents/schemas/outputs.py`, `invoke_fallback`; memory `tradingagents-schemas` |
| M4 | Vendor calls respect simulation end date (point-in-time) | `simulation_context.py`, `interface.route_to_vendor`; memory `tradingagents-dataflows` |
| M5 | Optional ticker anonymization in prompts/tool I/O | `tradingagents/anonymization/`; memory `tradingagents-anonymization` |
| M6 | Backtest applies signals with configurable cost model and metrics | `tradingagents/backtest/`; memory `tradingagents-backtest` |

---

## Empirical claims (require *your* run data — not new repo code)

| ID | Claim | Evidence |
|----|--------|----------|
| E1 | The **full** pipeline (`PAPER_ABLATION=full`) on **`RELIANCE.NS`** yields different agent vs buy-and-hold outcomes under **exogenous bear and bull calendar windows** | Frozen regime CSVs below + `scripts/backtest_regime_analysis.ipynb` |

---

## Regime definition (Frozen E1)

**Market regimes** are assigned **exogenously** from the underlying adjusted close path of **`RELIANCE.NS`** over each evaluation window, independent of agent signals or internal bull/bear **debate roles**.

| Label | Rule |
|-------|------|
| **Bear regime** | Total buy-and-hold return on the window **≤ −10%** (underlying close, first processed trading day → last). |
| **Bull regime** | Total buy-and-hold return on the window **≥ +10%**. |

Windows are chosen **before** backtests and recorded in `regime-timeranges`. Each regime run starts from **fresh paper cash** ($100,000); windows are **not** contiguous slices of one ledger.

**Distinction:** Internal **Bull Researcher** / **Bear Researcher** nodes are graph roles; **bear/bull regime** here refers only to the labeled calendar windows above.

---

### Frozen E1 (current manuscript inputs)

Write §4 Experiments against **these** artifacts unless you replace them after more runs:

| Field | Bear | Bull |
|--------|------|------|
| **Regime label** | Bear | Bull |
| **Calendar intent** | Aug 2024 – Jan 2025 | Jan 2025 – Jun 2025 |
| **Processed window** | `2024-08-01` .. `2025-01-03` | `2025-01-01` .. `2025-05-16` *(bull schedule truncated at last successful day)* |
| **Trading days processed** | 111 | 94 |
| **Ticker** | `RELIANCE.NS` | same |
| **Pipeline** | `PAPER_ABLATION=full` (default in `default_config.py`; all analysts + investment debate + risk) | same |
| **Initial cash** | $100,000 | $100,000 |
| **Cost model** | `zerodha_delivery`, `slippage_bps=0` | same |
| **LLM** | `qwen/qwen3.5-flash-02-23` (OpenRouter) | same |
| **Anonymization** | Enabled in runs (`STOCK_4264` in logs) | same |
| **Artifact CSV** | `results/dates-REL-aug-2024-jan-2025-bear-dates.csv` | `results/dates-REL-jan-2025-june-2025-bull-dates.csv` |
| **Run log** | `eval_results/dates-REL-aug-2024-jan-2025-bear-dates.log` | `eval_results/dates-REL-jan-2025-june-2025-bull-dates.log` |
| **Driver** | `scripts/backtest_mvp.py --ticker RELIANCE.NS --dates-csv <artifact>` | same |
| **Analysis** | `scripts/backtest_regime_analysis.ipynb`, `scripts/generate_paper_figures.py` | same |
| **Underlying B&H return** | −17.43% | +19.25% |
| **Agent total return** | −7.54% | +8.68% |
| **Ending equity** | $92,459.38 | $108,675.02 |
| **Max drawdown (last row)** | 5.11% | 0.47% |
| **Sharpe (last row)** | −3.12 | +2.62 |
| **Final signals (counts)** | SELL 76, HOLD 28, BUY 7 | SELL 68, HOLD 20, BUY 6 |

**Retired from paper scope** (see `results/_retired/README.md`): ablation CSVs, longitudinal `results/dates.csv`, `fig_ablation_*`, old `fig_dates_*`.

---

## Forbidden in camera-ready unless you have proof

- Metrics or plots that need **unimplemented** `ROADMAP.md` items (CBS calculator, rationale automation, LOB simulator, etc.).
- “State of the art” vs proprietary systems without a defined comparison protocol.
- Regime labels inferred from agent outlook columns (regimes are exogenous only).

---

## Changelog

| Date | Note |
|------|------|
| 2026-04-29 | Replaced CBS / held-out / cap-off rows; scoped to memory + user-generated run evidence. |
| 2026-04-30 | Dropped E2 empirical row; added Frozen E1 table for ablation `results/` + scripts. |
| 2026-05-28 | **Regime freeze:** bear + bull CSVs; ablation artifacts retired; E1 = agent vs B&H under exogenous regimes. |
