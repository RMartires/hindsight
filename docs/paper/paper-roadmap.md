# Hindsight 20/20 — Paper roadmap & progress

> How to write about **what already exists** in this repo. Scope is bounded by **`.cursor/memory.md`**: that index links to module notes (`memory/*.md`) that describe the real codebase.
>
> **Engineering gaps** (future features not yet built) live in repo-root **`ROADMAP.md`**. They are **not** paper tasks here. If the manuscript cites a capability, it must match a module described in memory.

**Submission draft (PDF / LaTeX source of truth):** [manuscript.md](manuscript.md)

**Last updated:** 2026-04-30.

**Done since last reset:** full **`manuscript.md`** draft (§1–§5 + Contributions); **[Frozen E1](claim-evidence-map.md)** table + empirical Table 1; **§4.2** pins LLM **`qwen/qwen3.5-flash-02-23`**; **`scripts/generate_paper_figures.py`** builds **`figures/`** (ablation + `dates.csv` panels, PDF/PNG); empirical row **E2** removed from claim map.

**Blocking submission:** submit **`docs/paper/submission/Hindsight2020_AlgorithmicFinance_IOS_submission.pdf`** or `.docx` via **[Algorithmic Finance](https://www.iospress.com/catalog/journals/algorithmic-finance)** portal — replace bracketed author placeholders in **`ios_manuscript.md`** then rebuild; complete declarations; **decline optional gold OA** for \$0.

**Non-blocking / queued:** expand **`bib-seed.bib`** (explicitly deferred); optional **DAG** figure; README reproducibility pointer; frozen **git commit** hash after submission freeze.

---

## Venue / template / anonymization

**Not inferable from `results/`:** fine-grained layout (margins, heading numbering), submission-portal fields, and declaration checkboxes come from **[Algorithmic Finance — Instructions](https://www.iospress.com/catalog/journals/algorithmic-finance)** only.

### **Chosen venue:** [Algorithmic Finance](https://www.iospress.com/catalog/journals/algorithmic-finance) (IOS Press)

| Topic | Note |
|-------|------|
| **Author fees** | **No publication fee** on default track; [optional gold OA is paid](https://www.iospress.com/catalog/journals/algorithmic-finance)—skip to stay at **\$0** |
| **Submission file** | IOS: manuscript as **one file** (PDF or Word or zip) **with tables and figures included**, unless their current form specifies otherwise—follow live author instructions |
| **Abstract** | **≤200 words** (current [`manuscript.md`](manuscript.md) abstract ≈ **218 words**—needs a short trim) |
| **References** | **Harvard** style (adjust from draft author–year prose / BibTeX pipeline when exporting) |
| **Still on you** | Portal login, corresponding-author contact, copyright / competing-interest declarations, **final read**, ticking **no paid OA** at acceptance if offered |

**Alternatives (not chosen):** Decision Support Systems; Expert Systems with Applications; Knowledge-Based Systems; Neural Computing and Applications — see older notes if you switch journals.

**Visibility without APC:** post an **[arXiv](https://arxiv.org/)** preprint + **[Zenodo](https://zenodo.org/)** artifact DOIs in parallel (lawful under journal policy—check **[Sherpa Romeo](https://v2.sherpa.ac.uk/romeo/)** or the journal’s preprint rules).

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
| MVP / ablation scripts, analysis notebooks, paper figures CLI | `scripts` (**includes `generate_paper_figures.py`**) |
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
| [claim-evidence-map.md](claim-evidence-map.md) | Claims ↔ evidence + **Frozen E1** artifact table |
| [bib-seed.bib](bib-seed.bib) | Starter BibTeX (§2 cites seed keys; broaden when venue set) |
| [submission/](submission/) | **Algorithmic Finance** IOS package (`ios_manuscript.md`, PDF/DOCX, `build_ios_package.sh`) |

---

## Progress toward `paper.pdf`

**Snapshot**

| Track | Status |
|-------|--------|
| Prose (`manuscript.md`) | §1–§5 + Contributions drafted |
| Empirical freeze | [Frozen E1](claim-evidence-map.md) + Table 1 (ending equity) |
| Figures | ✅ **`figures/`** — `{fig_ablation_*, fig_dates_*}.{pdf,png}` |
| LLM reproducibility | **`qwen/qwen3.5-flash-02-23`** named in §4.2 (+ env appendix optional) |
| Bibliography | Starter only — expansion **deferred** |
| Target venue | ✅ **[Algorithmic Finance](https://www.iospress.com/catalog/journals/algorithmic-finance)** (IOS Press, \$0 default; decline optional OA) |
| IOS-formatted submission PDF / Word | ✅ | **`docs/paper/submission/`** — run **`build_ios_package.sh`** |

**Rule:** Favor claims in `manuscript.md` + [STORY_LOCK.md](STORY_LOCK.md). Empirical rows need real artifacts ([claim-evidence-map.md](claim-evidence-map.md) **E1** + **Frozen E1** table).

**Legend:** ✅ done · 🟡 draft / needs review · ⬜ not started · 🔁 optional / venue-dependent

### Manuscript (`manuscript.md`)

| Section | Status | Notes / artifact |
|--------|--------|------------------|
| Title | 🟡 | Working title; tighten for venue word limit |
| Abstract | 🟡 | ≤200 words for IOS — trimmed in **`submission/ios_manuscript.md`** and synced here |
| Contributions | 🟡 | Numbered list at document end |
| 1. Introduction | 🟡 | Points to §2–§5 |
| 2. Related Work | 🟡 | Uses **`bib-seed.bib`** keys only — broaden optionally; **Harvard** list at export |
| 3. Method / System | 🟡 | Full §3 drafted; spot-check vs `.cursor/memory.md` before submission |
| 4. Experiments | 🟡 | Frozen E1, Table 1, **`qwen/qwen3.5-flash-02-23`**, §4.4 figure script command |
| 5. Conclusion + limitations | 🟡 | Mirrors shipped scope + ROADMAP honest gaps |
| Appendix / supplementary | 🔁 | Optional: `.env` snapshot for runs, DAG figure |

### Figures and tables

| Item | Status | Source |
|------|--------|--------|
| Pipeline / DAG figure | ⬜ | LangGraph topology (`GraphSetup`) — optional for venue |
| Ablation equity / drawdown / signal counts | ✅ | **`figures/fig_ablation_*.pdf`** (+ `.png`) |
| Schedule (`dates.csv`) portfolio / signals / outlook | ✅ | **`figures/fig_dates_*.pdf`** |
| Ending-equity table | ✅ | **Table 1** in **`manuscript.md`** §4.3 |
| Extended metrics table | 🔁 | `tradingagents.backtest.metrics` / notebooks — optional extras |
| Qualitative trace | 🔁 | Not claimed (E2 removed); **`full_states_log_*.json`** unused |

### Bibliography and formatting

| Item | Status | Notes |
|------|--------|-------|
| Expand `bib-seed.bib` / venue `.bib` | 🔁 | **Deferred**; export references in **Harvard** style for IOS |
| Citation pass on intro + related | 🟡 | §2 aligned with seed keys; rerun after bib grows |
| Figures embedded / captioned per IOS | ✅ | Embedded in **`submission/*.pdf`**; **`figures/*.pdf`** in bundle |
| Venue template (LaTeX / Word) | ✅ | **`ios_manuscript.md`** → PDF/DOCX via pandoc |
| Final PDF build | ✅ | **`docs/paper/submission/Hindsight2020_AlgorithmicFinance_IOS_submission.pdf`** |

### Repo / supplementary (if venue allows)

| Item | Status | Notes |
|------|--------|-------|
| README pointer to paper + artifact layout | 🔁 | |
| Frozen commit hash for “reproducibility” blurb | ⬜ | After experiments frozen |
| Ethics / data use statement | 🔁 | Venue-dependent |

---

## Rule of thumb

If a sentence in the paper implies a metric, plot, or module **not** described in `.cursor/memory.md`, either **cut the claim**, **implement it and update memory via the `update-memory` skill**, or **say it is future work** and point readers to `ROADMAP.md`.
