# Hindsight 20/20 — Paper guide & progress

> How to write about **what already exists** in this repo. Scope is bounded by **`.cursor/memory.md`**: that index links to module notes (`memory/*.md`) that describe the real codebase.
>
> **Engineering gaps** (future features, analytics modules not yet built) live only in **`ROADMAP.md`**. They are **not** paper tasks here. If the manuscript cites a capability, it must match a module described in memory.

**Last updated:** 2026-04-29 — manuscript sections through **§2 Related Work** drafted in this file; Method/Experiments/Conclusion not yet.

---

## Use these anchors

1. **`.cursor/memory.md`** — what components exist and where (backend, engine, scripts, tests, artifacts).
2. **`docs/paper/`** — story lock, outline, bib seed, claim–evidence (aligned with *existing* artifacts).
3. **This file (`PAPER_ROADMAP.md`)** — working **abstract & contributions** prose plus **progress toward `paper.pdf`**.
4. **`ROADMAP.md`** — code/product backlog; **do not** treat as paper deliverables unless you implement and document in memory.

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
| [STORY_LOCK.md](docs/paper/STORY_LOCK.md) | Title, pitch, and **memory-backed** contribution table (S1–S5) |
| [outline.md](docs/paper/outline.md) | Section skeleton referencing real modules |
| [claim-evidence-map.md](docs/paper/claim-evidence-map.md) | Claims ↔ evidence **you can produce from existing code + logs + CSVs** |
| [bib-seed.bib](docs/paper/bib-seed.bib) | Starter citations for Related Work |

**Submission draft + PDF checklist:** below in this file (not separate markdown).

---

## Working title (submission draft)

*Point-in-Time Multi-Agent LLM Trading: A Reproducible LangGraph Stack with Ablations and Fair Backtesting*

*(Refine with co-authors and venue limits on length/style.)*

---

## Abstract (submission draft)

Large language models are increasingly used in financial decision pipelines, but published systems are often hard to reproduce, weakly specified at the tool-and-data boundary, and difficult to compare under controlled depth-of-reasoning ablations on true historical “as of” dates. We present **Hindsight 20/20**, an open-source **LangGraph** implementation for single-asset trading research that composes specialist analysts, multi-view debate, and risk critique into a unified decision graph. Each stage can emit **structured outputs** validated against **Pydantic** schemas, improving auditability of intermediate reasoning in run logs. Market and context retrieval are routed through a vendor layer that enforces a **simulation end date** for point-in-time access, with optional **ticker anonymization** to reduce trivial string leakage in prompts and tool payloads. We pair the live pipeline with a **paper backtest** that replays daily signals through a configurable cost model and standard performance metrics, and we ship **preset ablations** (`a1`, `a2`, `a3`, `full`) wired to the same engine via `PAPER_ABLATION`, enabling reproducible depth comparisons without forking the codebase. The repository includes scripts and notebooks for batch ablation runs and offline analysis of equity artifacts and structured state logs. Together, the stack is intended as a reproducible baseline for research on multi-agent LLM trading under explicit temporal and disclosure controls, with tracing hooks compatible with **Langfuse** for operational debugging rather than as a standalone scientific contribution.

---

## 1. Introduction (submission draft)

*Background literature is summarized in §2; starter keys live in [bib-seed.bib](docs/paper/bib-seed.bib) (expand before camera-ready).*

Researchers and practitioners are experimenting with large language models (LLMs) as planners, analysts, and debaters inside trading and portfolio workflows. A single-asset, day-ahead setting is a natural testbed: the model must interpret noisy text and tabular context, call tools, and emit a discrete action whose quality can be checked later against realized prices. Yet building *research-grade* stacks in this space is still brittle. Systems are often described at a high level while leaving tool wiring, data routing, and temporal constraints implicit, which makes leakage across train/serving or “as of” boundaries hard to audit. Worse, when teams compare “more agents” vs “fewer agents,” they frequently fork codepaths or change prompts ad hoc, so it is unclear whether measured differences come from added reasoning depth or from an unrelated implementation drift.

We target **historical, point-in-time** use: on each trade date the pipeline may only consume information available on or before that date. That requirement is easy to state and hard to enforce consistently once multiple vendor adapters, caches, and tool schemas are in play. We also care about **traceability**: downstream consumers should be able to inspect what each stage produced without scraping free-form blobs that are expensive to validate or diff across runs.

This paper presents **Hindsight 20/20**, an open-source implementation built on **LangGraph**, focused on *reproducibility and fair comparison* rather than on claiming a new state-of-the-art return. The same graph drives live UI/CLI runs and scripted backtests. Analyst and researcher modules gather context through a vendor layer governed by a **simulation end date**; **structured outputs** (Pydantic schemas with structured-output fallbacks) make stage artifacts inspectable. For studies that seek to reduce direct ticker exposure in model-visible strings, optional **anonymization** can be enabled via configuration. **Preset ablations** (`a1`–`full`), selected through a single environment-controlled flag, vary which analysts and debate stages execute while importing the same engine code, so ablation studies do not require parallel forks. A **paper backtest** replays produced signals through a ledger with configurable fees and standard performance metrics, emitting CSV-style artifacts and pairing with notebooks for offline analysis.

**Structure.** §2 surveys related themes at a high level. §3 describes the system as implemented—graph orchestration, tools and data routing, structured outputs, temporal policy, anonymization, ablations, and the backtest harness—grounded in the public codebase (see **`.cursor/memory.md`** for module-level pointers). §4 outlines an empirical protocol that uses existing scripts and stored run artifacts; concrete tables and figures should reflect runs you have actually executed. §5 concludes with limitations honest to the current design (for example single-asset paper execution, vendor dependence). The numbered **contributions** below mirror the claims we intend to support from the repository and logs.

---

## 2. Related Work (submission draft)

*Citation style here is author–year for readability; map to BibTeX keys in [bib-seed.bib](docs/paper/bib-seed.bib) (`xiao2024tradingagents`, `yu2023finmem`, `yang2023fingpt`). The seed file is intentionally small—add point-in-time finance, memorization, and agent-systems citations before submission.*

**LLM agents for trading and finance.** A line of recent work studies autonomous or semi-autonomous LLM agents for market analysis and trading decisions. Xiao et al. introduce **TradingAgents**, a multi-agent framework in which specialized roles debate and coordinate toward trading outputs, illustrating how orchestrated LLM workflows can structure financial reasoning beyond a single chat completion (Xiao et al., 2024). Yu et al. propose **FinMem**, which combines layered memory and “character” design to steer an LLM trading agent, emphasizing long-horizon interaction patterns and task-specific scaffolding (Yu et al., 2023). Broader open financial LLM efforts such as **FinGPT** lower the barrier to experimenting with finance-tuned models and data pipelines in public repositories (Yang et al., 2023). These contributions are largely **algorithmic and modeling-focused**: they motivate multi-role graphs, tool use, and memory-rich agents. Our work is complementary: we foreground **reproducible systems engineering**—a single LangGraph codepath, **preset ablations** on that path, **schema-constrained stage outputs**, and a **scriptable paper backtest** so that comparisons of pipeline depth are not confounded by forked implementations.

**Point-in-time data, leakage, and memorization.** Empirical finance and applied ML have long stressed that conclusions can be invalidated when features are accidentally built with future information or when identifiers leak test-set signal. Large models exacerbate the problem in two ways: tool-augmented agents can issue requests whose temporal semantics are easy to mis-specify across vendors, and strong LMs can exploit trivial cues (for example recurring ticker strings or corpus-regularities) unless experiments control what the model sees. Survey papers and venue-specific benchmarks are still catching up to fully standardized “as of” protocols for LLM agents; we therefore treat an explicit **simulation end date**, centralized vendor routing, and **optional ticker anonymization** as first-class implementation requirements rather than afterthoughts. *(Add classic PIT / leakage references from `bib-seed.bib` when expanded.)*

**Multi-agent depth, cost, and fair ablation.** Each additional analyst, debate round, or risk critique typically multiplies LLM calls and latency. Prior agent frameworks demonstrate that deeper graphs can improve flexibility but rarely ship a **small, named set of ablation modes** wired to one implementation, which makes it difficult to attribute benchmark shifts to architecture versus accidental prompt or tooling drift. Our stack adopts the multi-agent idiom in the spirit of TradingAgents- and FinMem-style systems, but emphasizes **controlled depth-of-pipeline studies**: toggling phases through configuration while sharing code, logs, and backtest drivers.

**Execution realism and evaluation harnesses.** Research prototypes often report model-side decisions without a transparent link to **fees, ledger state, and realized mark-to-market assumptions**—choices that dominate single-asset P&L in realistic settings. Open financial model stacks (Yang et al., 2023) improve accessibility of *models*; we instead document a **paper-ledger backtest** with configurable costs and standard summary metrics, so that agent outputs can be turned into equity curves and tables under stated assumptions. This does not simulate full limit-order-book microstructure; it **matches the fidelity of the shipped code** and keeps evaluation claims auditable.

**Positioning.** Relative to Xiao et al. (2024), Yu et al. (2023), and Yang et al. (2023), Hindsight 20/20 does not introduce a new standalone monetary benchmark winner. It contributes an **open, memory-aligned implementation narrative**: multi-agent LangGraph orchestration, structured outputs, temporal and anonymization controls, preset ablations, and a fee-aware backtest harness suitable for reporting results tied to **concrete artifacts** (CSVs, logs, notebooks).

---

## Contributions (submission-shaped)

Each item maps to **S1–S5** in [STORY_LOCK.md](docs/paper/STORY_LOCK.md) and to [claim-evidence-map.md](docs/paper/claim-evidence-map.md) (M1–M6).

1. **Multi-agent decision graph.** We describe a LangGraph-orchestrated pipeline that routes single-stock decisions through analyst modules, investment and risk debate stages, and downstream trading logic so that depth and participation can be varied within one codepath (S1 / M1).

2. **Controlled ablations on the same engine.** We contribute preset ablation modes that toggle which analysts and debate stages run, selected via `PAPER_ABLATION`, supporting reproducible comparisons of pipeline depth without maintaining parallel implementations (S2 / M2).

3. **Structured stage outputs.** We integrate schema-constrained LLM outputs (Pydantic models and structured parsing fallbacks) so that intermediate decisions and rationales are machine-checkable and easy to retain in graph state and logs (S3 / M3).

4. **Point-in-time data policy and optional anonymization.** We document a simulation-date cap and vendor routing that bound requests to information available on each trade date, and optional ticker anonymization for experiments that seek to limit direct ticker exposure in model-visible text (S4 / M4–M5).

5. **Backtest harness and analysis artifacts.** We pair the agent stack with a paper-ledger backtest, configurable fees, standard return and risk metrics, and CSV-oriented artifacts produced by the shipped MVP and ablation driver scripts, enabling evaluation from stored runs and notebooks (S5 / M6).

**Not claimed here:** superiority over proprietary or undisclosed systems; new predictability theory; or metrics that require features listed only as future work in `ROADMAP.md`.

---

## Progress toward `paper.pdf`

**Snapshot (keep in sync when you add sections):** **Drafted here:** working title, Abstract, §1 Introduction, §2 Related Work, numbered Contributions. **Still outline-only / not drafted in this file:** §3 Method, §4 Experiments, §5 Conclusion. **Not started:** figures, venue LaTeX, final PDF. **`bib-seed.bib`:** three arXiv entries; expand before camera-ready (PIT/leakage/etc.).

**Rule:** Favor claims in this file + [STORY_LOCK.md](docs/paper/STORY_LOCK.md). Empirical rows need real artifacts ([claim-evidence-map.md](docs/paper/claim-evidence-map.md) E1–E2).

**Legend:** ✅ done · 🟡 draft / needs review · ⬜ not started · 🔁 optional / venue-dependent

### Manuscript sections

| Section | Status | Notes / artifact |
|--------|--------|------------------|
| Title | 🟡 | Working title above; venue length/style |
| Abstract | 🟡 | First draft above |
| Contributions (intro-style list) | 🟡 | Numbered list above |
| 1. Introduction | 🟡 | First draft; cross-ref §2 |
| 2. Related Work | 🟡 | First draft §2; expand `bib-seed.bib` before CR |
| 3. Method / System | ⬜ | Map to `memory/*.md` per `outline.md` |
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
| Merge `bib-seed.bib` into master `.bib` | ⬜ | Add venue-required related work |
| Citation pass on intro + related | 🟡 | §2 uses seed keys only; add PIT/leakage/agent-cost cites |
| Venue template (LaTeX / Word) | ⬜ | Create or link project for `paper.pdf` |
| Final PDF build | ⬜ | Overleaf / local `latexmk` |

### Repo / supplementary (if venue allows)

| Item | Status | Notes |
|------|--------|-------|
| README pointer to paper + artifact layout | 🔁 | |
| Frozen commit hash for “reproducibility” blurb | ⬜ | After experiments frozen |
| Ethics / data use statement | 🔁 | Venue-dependent |

---

## Rule of thumb

If a sentence in the paper implies a metric, plot, or module **not** described in `.cursor/memory.md`, either **cut the claim**, **implement it and update memory via the `update-memory` skill**, or **say it is future work** and point readers to `ROADMAP.md`.
