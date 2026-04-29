# Paper outline (section skeleton)

Companion to [STORY_LOCK.md](STORY_LOCK.md) (Phase 0) and [../PAPER_ROADMAP.md](../../PAPER_ROADMAP.md) (full roadmap). **Do not expand claims** beyond [claim-evidence-map.md](claim-evidence-map.md).

---

## Abstract (after experiments freeze)

- Sentence 1: one-line pitch from `STORY_LOCK.md`.
- Task / gap: multi-agent LLM trading evaluations optimize architecture, not **latency-adjusted** coordination value.
- Method: CBS + `a1`…`full` lattice + temporal cap + anonymization + fee-aware backtest.
- Result: one **pre-registered** headline number from R2 or R6.
- Takeaway: when to prefer single-agent vs full stack **in basis points / regime language**.

---

## 1. Introduction

- **§1.1** Task + stakes: single-stock LLM decisions; **raw alpha is insufficient** without latency and leakage controls.
- **§1.2** Three challenges (memorization, lookahead/vendor time travel, coordination latency × volatility) — each **one paragraph**, cite cluster B then A.
- **§1.3** Our answer: **CBS** + lattice; **fair** measurement (C3); point to teaser figure.
- **§1.4** Empirical preview: multi-ticker × periods (no numbers until frozen).
- **§1.5** Contributions: **C1–C4** verbatim list from `STORY_LOCK.md`.

---

## 2. Related Work

- §2.1 Cluster A (agents for trading).
- §2.2 Cluster B (leakage / memorization / point-in-time).
- §2.3 Cluster C (coordination cost — CBS novelty lives here).
- §2.4 Cluster D (execution / fees — short).

---

## 3. Method (or split 3–4 + 5 CBS)

- §3.1 **System overview** — `TradingAgentsGraph`, LangGraph, streaming vs `propagate`.
- §3.2 **Stages** — analysts, debate, trader, risk debate, judge; cite `graph/setup.py`.
- §3.3 **Structured outputs** — `schemas/outputs.py`; JSON-in-state convention.
- §3.4 **Temporal policy** — `effective_simulation_end_date_str`, `clamp_date_range_eod`, news date rules.
- §3.5 **Anonymization** — `TickerMapper`, deanonymize/scrub path.
- §3.6 **Backtest / execution** — `PaperLedger`, Zerodha fees, gross vs net.
- **§4 or §5 CBS** — definition, units, latency measurement protocol (Langfuse / callbacks), σ per second from OHLCV; **decision rule** vs expected alpha.

---

## 4. Experiments

- §4.1 Setup: tickers, periods, seeds, models, costs, B&H (`buy_and_hold_total_return`).
- §4.2 Main: full vs B&H; ablation table.
- §4.3 CBS validation (R2): held-out protocol declared **before** runs.
- §4.4 Robustness: anonymization A/B; optional US ticker appendix.
- §4.5 Negative regime (R1): at least one case where shallow ablation wins.

---

## 5. Conclusion

- Three bullets: CBS, lattice + fairness, empirical prediction.
- One limitation: single-asset, no LOB (`ROADMAP.md` §4.1).

---

## Appendix (sketch)

- Cap-off vs cap-on (R3).
- Extended tables per ticker.
- Hyperparameters and exact `PAPER_ABLATION` / env snapshot per run.
