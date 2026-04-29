# Paper outline (memory-aligned)

Companion to [STORY_LOCK.md](STORY_LOCK.md). Submission draft + PDF progress: [../../PAPER_ROADMAP.md](../../PAPER_ROADMAP.md). Sections cite **what exists** per **`.cursor/memory.md`**.

**Do not** commit to experiments or metrics that require `ROADMAP.md` features not yet built unless you implement them and update memory.

---

## Abstract

- Problem: single-stock, historical “as of” decisions with LLM agents; need reproducibility and fair data use.
- Approach: LangGraph multi-agent stack + ablations + structured outputs + simulation cap + optional anonymization + paper backtest (**memory:** graph, agents, schemas, dataflows, anonymization, backtest).
- Evidence: point to **your** ablation/equity results (CSVs/notebooks), not hypothetical tables.

---

## 1. Introduction

- Task and why point-in-time + traceability matter.
- Contributions = **S1–S5** from `STORY_LOCK.md` (all memory-backed).

**Draft prose:** [../../PAPER_ROADMAP.md](../../PAPER_ROADMAP.md) §1 Introduction.

---

## 2. Related Work

- Multi-agent LLM finance stacks; leakage/memorization; execution realism.
- **We position** on implemented controls (temporal cap, anonymization, structured outputs, fees), not on unshipped analytics from `ROADMAP.md`.

**Draft prose:** [../../PAPER_ROADMAP.md](../../PAPER_ROADMAP.md) §2 Related Work.

---

## 3. Method / System

Map subsections to memory notes (paths from `memory/*.md`):

- **Architecture:** `TradingAgentsGraph`, LangGraph, streaming vs `propagate` — `tradingagents-graph`
- **Stages and tools:** `tradingagents-agents`, `tradingagents-dataflows`
- **Structured outputs:** `tradingagents-schemas`, `tradingagents-llm-clients`
- **Temporal policy and vendors:** `tradingagents-dataflows`
- **Anonymization:** `tradingagents-anonymization`
- **Backtest and metrics:** `tradingagents-backtest`
- **Ablations:** `config-and-env`, `paper_ablation`
- **(Optional)** UI + SSE demo: `backend`, `frontend` — supplementary only unless core to the venue

---

## 4. Experiments

- **Setup:** models (env), tickers/dates, `PAPER_ABLATION`, cost model — from `scripts/backtest_mvp.py` / `backtest_mvp_ablations.py` (`memory/scripts`, `tradingagents-backtest`).
- **Results:** tables/figures from **existing** `equity.csv` / `results/` runs and `backtest_ablation_analysis.ipynb`.
- **No requirement** for CBS curves, automated rationale scores, or cap-off A/B unless you add them as experiments **and** the code is real (then update memory).

---

## 5. Conclusion

- Restate S1–S5; limitations from actual design (single-asset paper book, BM25 memory, vendor dependence, etc.) — see `memory/overview.md` / `ROADMAP.md` for honest “future work” language.

---

## Appendix (optional)

- Hyperparameters, env snapshot, example `full_states_log` excerpt.
- **Future work** may cite `ROADMAP.md`; keep distinct from **done** system description.
