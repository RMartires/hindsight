# Manuscript (draft — export to PDF / LaTeX)

**Purpose:** Submission-facing prose only. Scope and checklist live in [paper-roadmap.md](paper-roadmap.md). Claims must match **`.cursor/memory.md`**.

**Last updated:** 2026-04-30.

**PDF:** Pandoc alone is not enough — it needs a LaTeX engine on your `PATH`.

1. **Recommended (Homebrew):** `brew install tectonic` then from repo root:
   `pandoc docs/paper/manuscript.md -o paper-draft.pdf --pdf-engine=tectonic`
2. **Classic TeX Live:** install BasicTeX or MacTeX, then ensure `pdflatex` is on `PATH` (often `export PATH="/Library/TeX/texbin:$PATH"`), then the plain `pandoc ... -o paper-draft.pdf` works.
3. **No LaTeX:** `pandoc docs/paper/manuscript.md -o paper-draft.html --standalone` and print to PDF from a browser.

Or use your editor’s Markdown → PDF. **Help script:** `scripts/build_manuscript_pdf.sh` (uses `tectonic` if available).

---

## Working title

*Point-in-Time Multi-Agent LLM Trading: A Reproducible LangGraph Stack with Ablations and Fair Backtesting*

*(Refine with co-authors and venue limits on length/style.)*

---

## Abstract

Large language models are increasingly used in financial decision pipelines, but published systems are often hard to reproduce, weakly specified at the tool-and-data boundary, and difficult to compare under controlled depth-of-reasoning ablations on true historical “as of” dates. We present **Hindsight 20/20**, an open-source **LangGraph** implementation for single-asset trading research that composes specialist analysts, multi-view debate, and risk critique into a unified decision graph. Each stage can emit **structured outputs** validated against **Pydantic** schemas, improving auditability of intermediate reasoning in run logs. Market and context retrieval are routed through a vendor layer that enforces a **simulation end date** for point-in-time access, with optional **ticker anonymization** to reduce trivial string leakage in prompts and tool payloads. We pair the live pipeline with a **paper backtest** that replays daily signals through a configurable cost model and standard performance metrics, and we ship **preset ablations** (`a1`, `a2`, `a3`, `full`) wired to the same engine via `PAPER_ABLATION`, enabling reproducible depth comparisons without forking the codebase. The repository includes scripts and notebooks for batch ablation runs and offline analysis of equity artifacts and structured state logs. Together, the stack is intended as a reproducible baseline for research on multi-agent LLM trading under explicit temporal and disclosure controls, with tracing hooks compatible with **Langfuse** for operational debugging rather than as a standalone scientific contribution.

---

## 1. Introduction

*Background literature is summarized in §2; starter keys live in [bib-seed.bib](bib-seed.bib) (expand before camera-ready).*

Researchers and practitioners are experimenting with large language models (LLMs) as planners, analysts, and debaters inside trading and portfolio workflows. A single-asset, day-ahead setting is a natural testbed: the model must interpret noisy text and tabular context, call tools, and emit a discrete action whose quality can be checked later against realized prices. Yet building *research-grade* stacks in this space is still brittle. Systems are often described at a high level while leaving tool wiring, data routing, and temporal constraints implicit, which makes leakage across train/serving or “as of” boundaries hard to audit. Worse, when teams compare “more agents” vs “fewer agents,” they frequently fork codepaths or change prompts ad hoc, so it is unclear whether measured differences come from added reasoning depth or from an unrelated implementation drift.

We target **historical, point-in-time** use: on each trade date the pipeline may only consume information available on or before that date. That requirement is easy to state and hard to enforce consistently once multiple vendor adapters, caches, and tool schemas are in play. We also care about **traceability**: downstream consumers should be able to inspect what each stage produced without scraping free-form blobs that are expensive to validate or diff across runs.

This paper presents **Hindsight 20/20**, an open-source implementation built on **LangGraph**, focused on *reproducibility and fair comparison* rather than on claiming a new state-of-the-art return. The same graph drives live UI/CLI runs and scripted backtests. Analyst and researcher modules gather context through a vendor layer governed by a **simulation end date**; **structured outputs** (Pydantic schemas with structured-output fallbacks) make stage artifacts inspectable. For studies that seek to reduce direct ticker exposure in model-visible strings, optional **anonymization** can be enabled via configuration. **Preset ablations** (`a1`–`full`), selected through a single environment-controlled flag, vary which analysts and debate stages execute while importing the same engine code, so ablation studies do not require parallel forks. A **paper backtest** replays produced signals through a ledger with configurable fees and standard performance metrics, emitting CSV-style artifacts and pairing with notebooks for offline analysis.

**Structure.** §2 surveys related themes at a high level. §3 describes the system as implemented—graph orchestration, tools and data routing, structured outputs, temporal policy, anonymization, ablations, and the backtest harness—grounded in the public codebase (see **`.cursor/memory.md`** for module-level pointers). §4 reports a concrete evaluation protocol and results from stored CSV artifacts and companion notebooks (single ticker; expanded benchmarks deferred). §5 concludes with limitations honest to the current design. **Contributions** are listed at the end of this document.

---

## 2. Related Work

*Citation style here is author–year for readability; map to BibTeX keys in [bib-seed.bib](bib-seed.bib) (`xiao2024tradingagents`, `yu2023finmem`, `yang2023fingpt`). The seed file is intentionally small—add point-in-time finance, memorization, and agent-systems citations before submission.*

**LLM agents for trading and finance.** A line of recent work studies autonomous or semi-autonomous LLM agents for market analysis and trading decisions. Xiao et al. introduce **TradingAgents**, a multi-agent framework in which specialized roles debate and coordinate toward trading outputs, illustrating how orchestrated LLM workflows can structure financial reasoning beyond a single chat completion (Xiao et al., 2024). Yu et al. propose **FinMem**, which combines layered memory and “character” design to steer an LLM trading agent, emphasizing long-horizon interaction patterns and task-specific scaffolding (Yu et al., 2023). Broader open financial LLM efforts such as **FinGPT** lower the barrier to experimenting with finance-tuned models and data pipelines in public repositories (Yang et al., 2023). These contributions are largely **algorithmic and modeling-focused**: they motivate multi-role graphs, tool use, and memory-rich agents. Our work is complementary: we foreground **reproducible systems engineering**—a single LangGraph codepath, **preset ablations** on that path, **schema-constrained stage outputs**, and a **scriptable paper backtest** so that comparisons of pipeline depth are not confounded by forked implementations.

**Point-in-time data, leakage, and memorization.** Empirical finance and applied ML have long stressed that conclusions can be invalidated when features are accidentally built with future information or when identifiers leak test-set signal. Large models exacerbate the problem in two ways: tool-augmented agents can issue requests whose temporal semantics are easy to mis-specify across vendors, and strong LMs can exploit trivial cues (for example recurring ticker strings or corpus-regularities) unless experiments control what the model sees. Survey papers and venue-specific benchmarks are still catching up to fully standardized “as of” protocols for LLM agents; we therefore treat an explicit **simulation end date**, centralized vendor routing, and **optional ticker anonymization** as first-class implementation requirements rather than afterthoughts. *(Add classic PIT / leakage references from `bib-seed.bib` when expanded.)*

**Multi-agent depth, cost, and fair ablation.** Each additional analyst, debate round, or risk critique typically multiplies LLM calls and latency. Prior agent frameworks demonstrate that deeper graphs can improve flexibility but rarely ship a **small, named set of ablation modes** wired to one implementation, which makes it difficult to attribute benchmark shifts to architecture versus accidental prompt or tooling drift. Our stack adopts the multi-agent idiom in the spirit of TradingAgents- and FinMem-style systems, but emphasizes **controlled depth-of-pipeline studies**: toggling phases through configuration while sharing code, logs, and backtest drivers.

**Execution realism and evaluation harnesses.** Research prototypes often report model-side decisions without a transparent link to **fees, ledger state, and realized mark-to-market assumptions**—choices that dominate single-asset P&L in realistic settings. Open financial model stacks (Yang et al., 2023) improve accessibility of *models*; we instead document a **paper-ledger backtest** with configurable costs and standard summary metrics, so that agent outputs can be turned into equity curves and tables under stated assumptions. This does not simulate full limit-order-book microstructure; it **matches the fidelity of the shipped code** and keeps evaluation claims auditable.

**Positioning.** Relative to Xiao et al. (2024), Yu et al. (2023), and Yang et al. (2023), Hindsight 20/20 does not introduce a new standalone monetary benchmark winner. It contributes an **open, memory-aligned implementation narrative**: multi-agent LangGraph orchestration, structured outputs, temporal and anonymization controls, preset ablations, and a fee-aware backtest harness suitable for reporting results tied to **concrete artifacts** (CSVs, logs, notebooks).

---

## 3. Method / System

This section summarizes the **shipped** implementation at the level of architecture and interfaces; file-level pointers follow **`.cursor/memory.md`**.

### 3.1 Architecture

The runtime centers on **`TradingAgentsGraph`** (`tradingagents/graph/trading_graph.py`), which wires LangGraph nodes defined by **`GraphSetup`** (`tradingagents/graph/setup.py`) and **`ConditionalLogic`** (`tradingagents/graph/conditional_logic.py`)—specialist analysts, optional bull/bear investment debate, trader synthesis, optional risk debate and judge, and signal extraction toward an executable instruction. Propagation per trade date uses **`Propagator`** (`tradingagents/graph/propagation.py`) with **`Reflector`** and **`SignalProcessor`** hooks as configured. The same graph class backs interactive CLI/UI flows and scripted **`run_backtest_mvp`** runs so backtests exercise the same orchestration path as exploratory sessions.

### 3.2 Agents, tools, and data routing

Analyst modules (market, social/news, fundamentals, etc.) consume tools implemented on **`tradingagents.agents.utils.agent_utils`**—price history, indicators, fundamentals line items, news, and related feeds—backed by vendor adapters and caches under **`tradingagents/dataflows/`**. Configuration flows through **`set_config`** and **`default_config.py`** so provider choice and credentials remain centralized.

### 3.3 Structured stage outputs

Stages that call LLMs can request **schema-constrained** completions aligned with Pydantic models in **`tradingagents/schemas/`**, with **`invoke_fallback`** handling providers that do not reliably honor native structured output. Validated objects are merged into **LangGraph state**, which downstream nodes and logging can consume without ad hoc parsing of unstructured blobs—supporting design goals **S3** / **M3** even though we do not claim log-level empirical analyses here.

### 3.4 Point-in-time policy

**`effective_simulation_end_date_str`** and related helpers clamp vendor-facing reads so that, on date \(d\), tooling does not request post-\(d\) facts through the normal routing path (**M4**). Exact adapter semantics vary by source; the invariant we encode is an explicit simulation horizon wired through propagation rather than ad hoc date strings scattered across tools.

### 3.5 Optional ticker anonymization

When enabled, **`TickerMapper`** substitutes opaque identifiers for raw tickers in prompts and tool I/O suitable for anonymization-aware experiments (**M5**), reducing trivial symbol leakage without replacing fundamentals semantics inside adapters.

### 3.6 Preset ablations

**`PAPER_ABLATION`** selects among **`a1`**, **`a2`**, **`a3`**, and **`full`** (`tradingagents/paper_ablation.py`). **`apply_paper_ablation_to_config`** sets **`selected_analysts`**, **`run_investment_debate`**, and **`run_risk_phase`** in place:

| Preset | Analysts | Investment debate | Risk phase |
|--------|------------|-------------------|------------|
| `a1` | market only | off | off |
| `a2` | market, social, news, fundamentals | off | off |
| `a3` | four analysts | on | off |
| `full` | four analysts | on | on |

All presets share one codebase path (**S2** / **M2**).

### 3.7 Paper backtest harness

**`run_backtest_mvp`** (`tradingagents/backtest/runner.py`) iterates trading dates, calls **`graph.propagate`** per day, maps graph output to **`BUY` / `SELL` / `HOLD`** via **`SignalProcessor`** when **`use_llm_signal`** is enabled for ambiguous heuristics, and applies fills through **`PaperLedger`** with **`cost_model`** (`flat_bps`, **`zerodha_delivery`**, **`zerodha_intraday`**) and optional **`slippage_bps`** (**M6**). Scripts **`scripts/backtest_mvp.py`** and **`scripts/backtest_mvp_ablations.py`** build configs from **`.env`** / env overrides (LLM provider, fee knobs, ablation flag). Schedule mode (**`--dates-csv`**) atomically updates a wide CSV (signals, equity path, per-stage outlook snapshots where emitted); standalone runs write **`equity.csv`**, **`trades.csv`**, and **`summary.json`** under **`eval_results/<ticker>/backtest_mvp_<id>/`**.

### 3.8 Observability (non-empirical)

When Langfuse credentials are present, runs attach correlation metadata for debugging (**optional trace hooks**); we do not treat trace dashboards as experimental evidence in §4.

---

## 4. Experiments

### 4.1 Goals and scope

We illustrate the stack with **small-scale, fully reproducible** runs aligned with the **Frozen E1** artifact table in [claim-evidence-map.md](claim-evidence-map.md): **one Indian equity listing (`RELIANCE.NS`)**, cost assumptions recorded in outputs (**e.g. `zerodha_delivery`** with **`slippage_bps=0`** in the longitudinal CSV header), and **preset ablations** over a fixed calendar window. We report **ending paper equity** from stored CSVs; Sharpe, drawdown, and richer summaries can be recomputed in notebooks via **`tradingagents.backtest.metrics`**. We **do not** claim breadth across universes, regimes, or alternative LLMs—the goal is a documented baseline tied to files in **`results/`**.

### 4.2 Protocol

**Longitudinal schedule CSV.** **`scripts/backtest_mvp.py`** was run in **`--dates-csv`** mode to produce **`results/dates.csv`**: one row per calendar row in the schedule, **`processed`** flags, **`final_signal`**, ledger columns, risk-adjusted summary columns when populated, and per-analyst **outlook** fields mirroring structured state for qualitative inspection. **`scripts/backtest_analysis.ipynb`** loads this file for plots.

**Fixed-window ablations.** **`scripts/backtest_mvp_ablations.py`** loops **`a1` … `full`** over weekdays from **`2024-05-01`** through **`2024-06-28`**, writing **`results/{preset}_2024-05-01_2024-06-30_RELIANCE_NS.csv`** (filename uses the requested range endpoints). The bundled inline driver sets **`initial_cash=100,000`**, **`buy_fraction=1.0`**, and **`use_llm_signal=False`**, i.e. no LLM **`SignalProcessor`** fallback when the heuristic mapper is ambiguous. **`scripts/backtest_ablation_analysis.ipynb`** overlays equity curves and tabulates metrics.

**LLM.** Frozen E1 runs used **`qwen/qwen3.5-flash-02-23`** (OpenRouter model slug) per the active **`scripts/backtest_mvp.py`** / **`.env`** configuration when those CSVs were produced; pin **`QUICK_THINK_LLM`**, **`DEEP_THINK_LLM`**, and provider keys in an appendix if quick and deep models differ.

### 4.3 Results

**Ablations (May–June 2024, `RELIANCE.NS`).** Table 1 lists **ending portfolio value** after fees from the frozen CSVs (**initial cash $100,000**). Rankings are **not** stable extrapolations—two months on one name illustrate dispersion across pipeline depth only.

**Table 1.** Ending equity by ablation preset (frozen artifacts under **`results/`**).

| Preset | Ending equity (notional) |
|--------|-------------------------|
| `a1` | \$111,480.32 |
| `a2` | \$110,159.53 |
| `a3` | \$89,749.01 |
| `full` | \$103,026.10 |

Under these runs, **more pipeline depth is not monotone in return**: the **`a1`** (single-analyst, no debates) path finishes highest and **`a3`** (debates without risk) finishes lowest, suggesting interactions between signal variance, turnover, and fees—consistent with the need for controlled ablations rather than informal “add agents” comparisons.

**Longitudinal `dates.csv`.** The schedule CSV spans additional calendar rows; the **last processed row with populated ledger fields** in our artifact ends **`2024-07-29`** with equity **\$106,029.65** and reported **`total_return` ≈ 6.03%** over the logged schedule fragment—use **`backtest_analysis.ipynb`** for full curves, turnover, and cost decomposition.

### 4.4 Figures

Regenerate publication plots from **`results/`** without Jupyter::

```bash
MPLCONFIGDIR=.mpl_cache .venv/bin/python scripts/generate_paper_figures.py
```

This writes **`docs/paper/figures/`** (`fig_ablation_equity`, `fig_ablation_drawdown`, `fig_ablation_signal_counts`, `fig_dates_portfolio`, `fig_dates_signals_close`, `fig_dates_signal_transitions`, `fig_dates_outlook_heatmap`, `fig_dates_outlook_consensus`) as PDF and PNG; figures include a small suptitle with the LLM id (`--no-llm-label` to omit). **`scripts/backtest_analysis.ipynb`** and **`scripts/backtest_ablation_analysis.ipynb`** remain the exploratory counterparts. A **conceptual DAG** of LangGraph nodes can be drafted from **`GraphSetup`** for Figure 1 if the venue requires architecture artwork.

---

## 5. Conclusion

We presented **Hindsight 20/20**, an open LangGraph implementation for single-stock LLM trading research with **preset ablations**, **structured outputs**, **simulation-date-aware data routing**, optional **ticker anonymization**, and a **fee-aware paper backtest** producing CSV artifacts and notebooks. Empirically, we documented **Frozen E1** runs on **`RELIANCE.NS`**, showing how ending equity varies across **`a1`–`full`** on a two-month window while a richer **`dates.csv`** trace supports qualitative inspection of stage outlooks.

**Limitations.** Evaluation is **narrow** (one ticker, short horizon, environment-specific LLM and vendors). **`use_llm_signal`** was **disabled** in the bundled ablation driver, so reported paths emphasize deterministic heuristic mapping unless separately enabled. We do **not** simulate microstructure, partial fills, or portfolio-wide constraints; **`PaperLedger`** is a research scaffold, not a broker simulator. Future work includes broader universes, model sweeps, and features tracked in **`ROADMAP.md`** once implemented and reflected in memory—distinct from claims in this manuscript.

---

## Contributions

Each item maps to **S1–S5** in [STORY_LOCK.md](STORY_LOCK.md) and to [claim-evidence-map.md](claim-evidence-map.md) (M1–M6).

1. **Multi-agent decision graph.** We describe a LangGraph-orchestrated pipeline that routes single-stock decisions through analyst modules, investment and risk debate stages, and downstream trading logic so that depth and participation can be varied within one codepath (S1 / M1).

2. **Controlled ablations on the same engine.** We contribute preset ablation modes that toggle which analysts and debate stages run, selected via `PAPER_ABLATION`, supporting reproducible comparisons of pipeline depth without maintaining parallel implementations (S2 / M2).

3. **Structured stage outputs.** We integrate schema-constrained LLM outputs (Pydantic models and structured parsing fallbacks) so that intermediate decisions and rationales are machine-checkable and easy to retain in graph state and logs (S3 / M3).

4. **Point-in-time data policy and optional anonymization.** We document a simulation-date cap and vendor routing that bound requests to information available on each trade date, and optional ticker anonymization for experiments that seek to limit direct ticker exposure in model-visible text (S4 / M4–M5).

5. **Backtest harness and analysis artifacts.** We pair the agent stack with a paper-ledger backtest, configurable fees, standard return and risk metrics, and CSV-oriented artifacts produced by the shipped MVP and ablation driver scripts, enabling evaluation from stored runs and notebooks (S5 / M6).

**Not claimed here:** superiority over proprietary or undisclosed systems; new predictability theory; or metrics that require features listed only as future work in `ROADMAP.md`.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-04-29 | Split from root `PAPER_ROADMAP.md`; paper-only export target. |
| 2026-04-30 | Added §3 Method, §4 Experiments (Frozen E1 numbers), §5 Conclusion; aligned intro structure text. |
| 2026-04-30 | Fig export script + `docs/paper/figures/`; pinned LLM id Qwen 3.5 Flash (`qwen/qwen3.5-flash-02-23`) in §4. |
