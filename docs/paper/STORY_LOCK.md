# Phase 0 — Story lock

**Status:** locked for drafting (update only with co-author agreement).  
**Last updated:** 2026-04-29.

This file is the single source of truth for title, pitch, contributions, related-work positioning, and submission naming. Phase 2+ experiments must not expand claims beyond what maps to the [claim–evidence map](claim-evidence-map.md).

---

## 1. Title and pitch (§1.1)

### Primary title

**Coordination Breakeven Spread: When Multi-Agent LLM Trading Pays for Its Own Latency**

### Alternate titles (keep for rebuttal / venue-specific retitling)

1. *Coordination Breakeven Spread: A Latency-Adjusted Metric for Single-Stock Multi-Agent LLM Backtests*
2. *CBS: Measuring When Multi-Agent LLM Coordination Beats Single-Agent Mode Under Intraday Volatility*

### One-line pitch (reuse as Abstract sentence 1 and Intro Part-A closing)

We introduce **Coordination Breakeven Spread (CBS)**—a closed-form breakeven that compares expected per-decision alpha from deeper multi-agent coordination against **end-to-end LLM latency × intraday price volatility per second** plus **transaction cost in basis points**—and pair it with a reproducible **`a1`→`a2`→`a3`→`full` ablation lattice** so that **single-agent mode is preferred when expected alpha falls below CBS**, not when headlines prefer “more agents.”

### System naming (double-blind vs public)

| Context | Name |
|--------|------|
| Manuscript body (venue expects blind build) | Neutral: “our system,” “the baseline implementation,” or “an open-source LangGraph trading stack.” |
| Supplementary / code / GitHub / blog | **Hindsight 20/20** is fine and matches this repo. |
| Camera-ready / arXiv after acceptance | Authors may use **Hindsight 20/20** in title or subtitle if venue allows. |

**Locked rule:** Do not put the product name in the anonymized PDF title unless the venue explicitly allows de-anonymized titles.

---

## 2. Claimed contributions (§1.2)

Four **numbered contributions** for Abstract and Intro (contribution list). Everything else is **setup** or **empirical validation**.

| ID | Contribution | One-sentence statement | Primary artifact |
|----|----------------|------------------------|------------------|
| **C1** | **CBS metric** | CBS = (mean graph LLM latency in seconds × σ_price per second on the decision day) + cost_bps (aligned with `ROADMAP.md` §5.3); it is a **per-decision breakeven hurdle** for coordination depth. | Method §5 or §4.7 + Fig. CBS curve |
| **C2** | **Ablation lattice + auditability** | A four-level preset lattice (`a1`/`a2`/`a3`/`full` via `tradingagents/paper_ablation.py`) over the same engine with **Pydantic structured outputs** per stage (`tradingagents/schemas/outputs.py`). | Method + Table ablations |
| **C3** | **Fair measurement** | **Strict temporal cutoff** (`simulation_context`, `interface._clamp_vendor_args`) and **deterministic ticker anonymization** (`TickerMapper`) so CBS and ablations are not inflated by lookahead or verbatim-symbol memorization. | Method + appendix cap-off / anonymization runs |
| **C4** | **Predictive validation** | Across **multi-ticker × multi-period** backtests, CBS **ranks or predicts** which ablation wins on **held-out** segments (pre-specified metric: net total return or Sharpe; lock in Exp notebook before runs). | Exp 3 + correlation / calibration figure |

**Explicitly not a headline contribution (setup detail):**

- **Realistic fees / gross vs net** — Zerodha-style cost stack (`zerodha_fees.py`) and `gross_total_return` vs net in `summary.json`: **Method / reproducibility** only; one sentence in Abstract max.

---

## 3. Related work — clusters and “they X, we Y” (§1.3)

Each paragraph in Related Work will follow this order: **trading LLM stacks → lookahead / memorization → coordination cost → execution cost.**

### Cluster A — LLM agent stacks for trading

**Representative anchors (verify keys in [bib-seed.bib](bib-seed.bib)):** TradingAgents (multi-role firm metaphor), FinMem (layered memory agent), FinGPT (FinLLM ecosystem / data-centric framing). Add 2–4 more: e.g. FINCON, QuantAgent, PIXIU—fill from your target venue’s recent citations.

**They X, we Y:** *They* propose increasingly rich multi-agent or memory-augmented **architectures** and report **raw backtest performance**; *we* fix **a decision criterion (CBS)** for when deeper coordination is **not** worth its **latency × volatility** cost, on top of an **explicit ablation lattice** and **temporal + anonymization controls.*

### Cluster B — Lookahead and memorization in LLM finance

**Anchors:** calendar-aware evaluation in practitioner critiques; ticker- and entity-aware leakage in replayed news; structure around “point-in-time” data in quant—add canonical **PEAD / point-in-time** citations from your bibliography manager.

**They X, we Y:** *They* document **leakage** and **memorization** as threats; *we* **implement** a vendor-wide **simulation end date** clamp and **deterministic symbol anonymization** so CBS comparisons remain **interpretable** under those threats.

### Cluster C — Coordination cost in multi-agent LLM systems

**Anchors:** inference-cost-aware routing for MoE / multi-agent tool use; latency–quality tradeoffs in agentic workflows—add 3 recent **systems / NLP** papers (not necessarily finance).

**They X, we Y:** *They* optimize **tokens, routing, or wall clock** in generic agents; *we* give a **finance-native breakeven** that combines **measured per-graph latency** with **intraday price volatility per second** and **broker-realistic cost_bps**, tied to **trading ablations**.

### Cluster D — Realistic execution and transaction costs

**Anchors:** market microstructure texts or broker fee documentation; backtest frameworks that separate gross and net.

**They X, we Y:** *They* motivate **execution realism**; *we* adopt a **documented statutory + brokerage stack** and report **gross vs net** so CBS **does not** mix “paper alpha” with **ignored fees**.

---

## 4. Figure / section mapping (contribution → deliverable)

| Contribution | Main figure | Main table | Experiment ref. (`PAPER_ROADMAP` §4) |
|--------------|--------------|------------|--------------------------------------|
| C1 | CBS vs latency (regimes) | Ablation rows + CBS column | §4.2 |
| C2 | Pipeline + lattice diagram | Full ablation table | §4.1 |
| C3 | (optional) timeline of cap | Appendix: cap on/off | §4.1 + cap-off |
| C4 | Calibration: predicted vs actual winner | Held-out summary | §4.1 split + §4.5 |

---

## 5. BibTeX seed

See [bib-seed.bib](bib-seed.bib). Expand to ~30 entries before intro freeze; **do not** cite placeholders in submission PDF.

---

## 6. Changelog

| Date | Change |
|------|--------|
| 2026-04-29 | Phase 0 lock: title, pitch, four contributions, four related-work clusters, naming policy. |
