# Hindsight 20/20 — Paper roadmap & progress

> How to write about **what already exists** in this repo. Scope is bounded by **`.cursor/memory.md`**: that index links to module notes (`memory/*.md`) that describe the real codebase.
>
> **Engineering gaps** (future features not yet built) live in repo-root **`ROADMAP.md`**. They are **not** paper tasks here. If the manuscript cites a capability, it must match a module described in memory.

**Submission draft (PDF / LaTeX source of truth):** [manuscript.md](manuscript.md)

**Last updated:** 2026-04-29 — manuscript through **§2 Related Work** + contributions; Method / Experiments / Conclusion still to add in `manuscript.md`.

---

## Use these anchors

1. **`.cursor/memory.md`** — what components exist and where (backend, engine, scripts, tests, artifacts).
2. **`docs/paper/manuscript.md`** — prose to submit or port into a venue template.
3. **`docs/paper/`** (this folder) — story lock, outline, claim–evidence, bib seed, **this roadmap**.
4. **Repo `ROADMAP.md`** — code/product backlog; **do not** treat as paper deliverables unless you implement and document in memory.

---

## What you can write about without new code

All of the following are documented in the memory index:

| Topic | See memory note |
|--------|------------------|
| LangGraph orchestration, ablation presets (`a1`–`full`) | `tradingagents-graph`, `config-and-env` (`paper_ablation`) |
| Analyst / researcher / trader / risk roles + tools | `tradingagents-agents`, `tradingagents-dataflows` |
| Structured LLM outputs (Pydantic) | `tradingagents-schemas`, `tradingagents-llm-clients` |
| Simulation date cap (no lookahead), vendor routing | `tradingagents-dataflows` |
| Ticker anonymization (`TickerMapper`) | `tradingagents-anonymization` |
| Backtest runner, ledger, Zerodha-style fees, metrics | `tradingagents-backtest` |
| MVP / ablation scripts, analysis notebooks | `scripts` |
| Langfuse traces, correlation IDs | `tradingagents-observability`, `backend` |
| UI + SSE (if mentioned as demo only) | `frontend`, `backend` |

**Generated outputs to cite as evaluation artifacts:** `results/`, `eval_results/`, `full_states_log_*.json` (per `artifacts` memory note). Use whatever runs you already have; expanding tickers/periods is **experimentation**, not repo feature work.

---

## `docs/paper/` layout

| File | Role |
|------|------|
| [manuscript.md](manuscript.md) | **Paper draft** — export to PDF / copy into venue LaTeX |
| [paper-roadmap.md](paper-roadmap.md) | **This file** — scope, memory bounds, progress to PDF |
| [STORY_LOCK.md](STORY_LOCK.md) | Title, pitch, memory-backed contribution table (S1–S5) |
| [outline.md](outline.md) | Section skeleton referencing real modules |
| [claim-evidence-map.md](claim-evidence-map.md) | Claims ↔ evidence from code + logs + CSVs |
| [bib-seed.bib](bib-seed.bib) | Starter citations for Related Work |

---

## Progress toward `paper.pdf`

**Snapshot:** **In `manuscript.md`:** working title, Abstract, §1–§2, Contributions. **Not yet in `manuscript.md`:** §3 Method, §4 Experiments, §5 Conclusion. **Not started:** figures, venue LaTeX. **`bib-seed.bib`:** three arXiv entries; expand before camera-ready.

**Rule:** Favor claims in `manuscript.md` + [STORY_LOCK.md](STORY_LOCK.md). Empirical rows need real artifacts ([claim-evidence-map.md](claim-evidence-map.md) E1–E2).

**Legend:** ✅ done · 🟡 draft / needs review · ⬜ not started · 🔁 optional / venue-dependent

### Manuscript (`manuscript.md`)

| Section | Status | Notes / artifact |
|--------|--------|------------------|
| Title | 🟡 | Working title in manuscript |
| Abstract | 🟡 | First draft in manuscript |
| Contributions | 🟡 | Numbered list in manuscript |
| 1. Introduction | 🟡 | First draft |
| 2. Related Work | 🟡 | Expand `bib-seed.bib` before CR |
| 3. Method / System | ⬜ | Map to `memory/*.md` per [outline.md](outline.md) |
| 4. Experiments | ⬜ | Freeze E1: presets, tickers, windows, `results/` paths |
| 5. Conclusion + limitations | ⬜ | `memory/overview.md` / honest gaps |
| Appendix / supplementary | 🔁 | Env snapshot, hyperparams, log excerpt |

### Figures and tables

| Item | Status | Source idea (`STORY_LOCK.md`) |
|------|--------|-------------------------------|
| Pipeline / DAG figure | ⬜ | LangGraph topology |
| Ablation equity curves | ⬜ | `results/*.csv`, `scripts/backtest_ablation_analysis.ipynb` |
| Metrics table | ⬜ | `equity.csv`, schedule columns, metrics formulas |
| Qualitative trace (optional) | ⬜ | `full_states_log_*.json` |

### Bibliography and formatting

| Item | Status | Notes |
|------|--------|-------|
| Merge `bib-seed.bib` into master `.bib` | ⬜ | Venue-required related work |
| Citation pass on intro + related | 🟡 | §2 uses seed keys only |
| Venue template (LaTeX / Word) | ⬜ | Port `manuscript.md` → template → PDF |
| Final PDF build | ⬜ | `scripts/build_manuscript_pdf.sh` or `pandoc` + `tectonic` / `pdflatex` |

### Repo / supplementary (if venue allows)

| Item | Status | Notes |
|------|--------|-------|
| README pointer to paper + artifact layout | 🔁 | |
| Frozen commit hash for “reproducibility” blurb | ⬜ | After experiments frozen |
| Ethics / data use statement | 🔁 | Venue-dependent |

---

## Rule of thumb

If a sentence in the paper implies a metric, plot, or module **not** described in `.cursor/memory.md`, either **cut the claim**, **implement it and update memory via the `update-memory` skill**, or **say it is future work** and point readers to `ROADMAP.md`.
