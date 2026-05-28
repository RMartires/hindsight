# Paper outline (memory-aligned)

Companion to [STORY_LOCK.md](STORY_LOCK.md). **Manuscript:** [manuscript.md](manuscript.md). **Roadmap:** [paper-roadmap.md](paper-roadmap.md).

---

## Abstract

- Problem: reproducible LLM trading stacks; need fair as-of evaluation.
- Approach: LangGraph + structured outputs + PIT cap + anonymization + paper backtest.
- Evidence: **full** pipeline on **RELIANCE.NS** under **bear** (Aug 2024–Jan 2025) and **bull** (Jan–May 2025) windows; agent vs buy-and-hold.

---

## 1. Introduction

- Point-in-time + traceability; contributions **S1–S5**.

---

## 2. Related Work

- LLM trading agents; leakage; **evaluation under market regimes**; execution realism.
- Position on implemented controls, not unshipped `ROADMAP.md` items.

---

## 3. Method / System

- Architecture, tools, structured outputs, PIT, anonymization.
- **§3.6** optional one paragraph: `PAPER_ABLATION` hook exists; §4 uses **`full`** only.
- Backtest harness (`backtest_mvp.py --dates-csv`).

---

## 4. Experiments

- **Regime definition** (exogenous ±10% underlying return rule) — [claim-evidence-map.md](claim-evidence-map.md).
- **Protocol:** two independent $100k runs; `PAPER_ABLATION=full`; LLM pinned.
- **Results:** Table 1 (metrics), Table 2 (outlook breakdown); figures from `generate_paper_figures.py`.
- **Limitation:** bull window truncated at 2025-05-16 (API limits).

---

## 5. Conclusion

- S1–S5; narrow scope (one ticker, two windows); future universes / model sweeps → `ROADMAP.md`.

---

## Appendix (optional)

- Env snapshot; `PAPER_ABLATION` preset table for repo users only.
