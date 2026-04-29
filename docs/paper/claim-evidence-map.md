# Claim–evidence map (memory-aligned)

**Rule:** Each claim below must be supportable from **existing code and artifacts** described in **`.cursor/memory.md`**. Do not add rows that require features listed only in `ROADMAP.md` as not implemented.

**Last updated:** 2026-04-29.

---

## System / method claims (typically no new runs required to *describe*)

| ID | Claim | Evidence |
|----|--------|----------|
| M1 | Multi-agent pipeline with analysts → debate → trader → risk → final decision | `graph/setup.py`, `TradingAgentsGraph`; memory `tradingagents-graph`, `tradingagents-agents` |
| M2 | Four ablation presets change which phases/analysts run | `tradingagents/paper_ablation.py`; memory `config-and-env` |
| M3 | Stages emit structured JSON aligned to Pydantic models | `tradingagents/schemas/outputs.py`, `invoke_fallback`; memory `tradingagents-schemas` |
| M4 | Vendor calls respect simulation end date (point-in-time) | `simulation_context.py`, `interface.route_to_vendor`; memory `tradingagents-dataflows` |
| M5 | Optional ticker anonymization in prompts/tool I/O | `tradingagents/anonymization/`; memory `tradingagents-anonymization` |
| M6 | Backtest applies signals with configurable cost model and metrics | `tradingagents/backtest/`; memory `tradingagents-backtest` |

---

## Empirical claims (require *your* run data — not new repo code)

Only state what you have actually run. Examples:

| ID | Claim | Evidence |
|----|--------|----------|
| E1 | Ablation X vs Y differ on metric Z for ticker T and window W | Your `results/` or `eval_results/` CSVs + notebook |
| E2 | Structured literals appear in schedule / logs for traceability | `extract_structured_schedule_literals`, `full_states_log_*.json` |

Add rows **after** you freeze a table from real runs. Remove or downgrade any claim if the artifact is missing.

---

## Forbidden in camera-ready unless you have proof

- Metrics or plots that need **unimplemented** `ROADMAP.md` items (CBS calculator, rationale automation, LOB simulator, etc.).
- “State of the art” vs proprietary systems without a defined comparison protocol.

---

## Changelog

| Date | Note |
|------|------|
| 2026-04-29 | Replaced CBS / held-out / cap-off rows; scoped to memory + user-generated run evidence. |
