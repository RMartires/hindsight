# Hindsight 20/20 — Paper Roadmap

> Plan for turning the current TradingAgents implementation into a submission-quality paper.
> Parallel to `ROADMAP.md` (which tracks **code** gaps); this file tracks **paper** gaps — story, claims, figures, experiments, and review readiness.
> **Last updated:** April 29, 2026.
>
> **Phase 0 — complete:** Story lock artifacts live under `docs/paper/` — [STORY_LOCK.md](docs/paper/STORY_LOCK.md) (title, pitch, contributions, related-work “they X, we Y”, naming), [claim-evidence-map.md](docs/paper/claim-evidence-map.md), [outline.md](docs/paper/outline.md), [bib-seed.bib](docs/paper/bib-seed.bib).
>
> **Locked decisions (v1):**
> - **Framing:** *Coordination Breakeven Spread (CBS)* as a new decision metric for when multi-agent LLM coordination is worth its latency cost. The `a1`→`a2`→`a3`→`full` ablation lattice is the empirical instantiation. Strict temporal cutoff + anonymization are guarantees that make CBS measurable, not the headline.
> - **Target venue:** main ML/Finance conference, ~8–9 pp + appendix. Multi-ticker × multi-period sweep is required.
> - **Lead code artifact:** `tradingagents/` engine + `scripts/backtest_mvp_ablations.py`. The paper does **not** advertise the FastAPI/Next.js dashboard as a contribution; it is mentioned only as reproducibility tooling.

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Drafted / experiment data already on disk |
| 🔶 | Partial — outline or seed data exists, needs extension or polish |
| ❌ | Not yet started — greenfield writing or experiment work |

---

## Module 1 · Story & Positioning

### 1.1 Title and one-line pitch ✅
**What it is:** A reviewer-facing title that telegraphs the CBS contribution, plus a 1-sentence pitch that anchors every section opening.

**Locked in `docs/paper/STORY_LOCK.md`:**
- *Primary title:* "Coordination Breakeven Spread: When Multi-Agent LLM Trading Pays for Its Own Latency"
- *Two alternates* + *pitch* + *double-blind naming policy* (product name only in non-blind / supplementary).

**What to build:**
- [x] Lock the title (run two more variants past co-authors)
- [x] Lock the pitch and reuse it verbatim as the first sentence of the abstract and the last sentence of the intro's Part-A paragraph
- [x] Decide naming: keep "Hindsight 20/20" as the system name, or drop in favor of a neutral name for double-blind venues

---

### 1.2 Claimed contributions (locked list) ✅
**What it is:** The 4–5 contributions every reviewer should be able to recite after reading the abstract. Each contribution maps 1:1 to a section, a figure, and an experiment.

**Locked list — four headline contributions (`docs/paper/STORY_LOCK.md`):**
1. **C1 — CBS metric.** Per-decision breakeven: (mean graph LLM latency × σ_price per second on decision day) + cost_bps; aligns with `ROADMAP.md` §5.3.
2. **C2 — Ablation lattice + auditability.** `a1`/`a2`/`a3`/`full` via `tradingagents/paper_ablation.py` + Pydantic stages in `tradingagents/schemas/outputs.py`.
3. **C3 — Fair measurement.** Temporal cutoff (`simulation_context`, `interface._clamp_vendor_args`) + `TickerMapper` anonymization.
4. **C4 — Predictive validation.** CBS **ranks or predicts** winning ablation on **held-out** segments; multi-ticker × multi-period.

**Setup detail (not a numbered contribution):** Zerodha-style fees + gross vs net — Method / reproducibility only.

**What to build:**
- [x] Drop or merge any contribution that fails the claim-evidence check in §5
- [x] Decide whether contribution (4) is a "contribution" or just a setup detail (most likely setup detail at conference length)

---

### 1.3 Related-work clusters ✅
**What it is:** The 3–4 buckets we will position against. Each bucket needs ≥3 representative recent papers and a one-sentence "they X, we Y".

**Locked in `docs/paper/STORY_LOCK.md` §3 — four clusters (A–D)** with verbatim **they X, we Y** sentences. Paragraph order for the paper: **A → B → C → D**.

**BibTeX:** `docs/paper/bib-seed.bib` seeds TradingAgents (arXiv:2412.20138), FinMem (2311.13743), FinGPT (2306.06031); expand to ~30 before Related Work freeze.

**What to build:**
- [x] Build the BibTeX seed (target ~30 citations for an 8-page paper)
- [x] For each bucket, fill in the "they X, we Y" sentence to use verbatim in Related Work

---

## Module 2 · Section Drafting Plan

### 2.1 Abstract ❌
**What it is:** ≤200 words, written *after* the experiments freeze. Uses the locked pitch from §1.1 as sentence 1.

**What to build:**
- [ ] One-paragraph draft, structure: task → gap → contribution → method → headline number → take-away
- [ ] Verify every quantitative claim against the claim-evidence map in §5

---

### 2.2 Introduction ❌
**What it is:** ~1 page using the *technical-challenge-version-3 + pipeline-version-1* templates from `research-paper-writing/references/introduction.md`. Three challenges → one CBS contribution with multiple advantages.

**Outline (to draft paragraph-by-paragraph):**
- Para A — Task + application: deploying multi-agent LLM systems for single-stock decisions; raw alpha alone is the wrong success metric.
- Para B — Three challenges: (i) latency × volatility erodes alpha at decision time, (ii) memorization makes paper alpha look better than live alpha, (iii) lookahead in vendor APIs (e.g. yfinance returning "today" rows) silently inflates returns. Cite for each.
- Para C — Our pipeline: CBS metric + ablation lattice; temporal cutoff and anonymization make the ablation comparison fair. Reference the teaser figure (§3.1).
- Para D — Headline empirical result (one number per ticker × period; placeholder until experiments freeze).
- Para E — Contributions list (mirror §1.2).

**What to build:**
- [ ] Lock paragraph order and topic sentences before writing prose
- [ ] Adversarial pass: a reviewer who has not read past the introduction must be able to predict what every later section will show

---

### 2.3 Related Work ❌
**What it is:** ¾ page. One paragraph per bucket from §1.3, each ending with the "they X, we Y" sentence.

**What to build:**
- [ ] Paragraphs in the order: trading-LLM stacks → memorization/lookahead → coordination cost → execution cost
- [ ] Cut anything that is not directly contrasted with our contribution list

---

### 2.4 Method ❌
**What it is:** ~2 pages. Pipeline figure (§3.2) drives the section; everything else is sub-paragraphs annotating boxes in the figure.

**Outline:**
- §4.1 System overview — point at pipeline figure; cite engine entry `tradingagents.graph.trading_graph.TradingAgentsGraph`.
- §4.2 Stage definitions — analysts → researchers → trader → risk debators → judge; cite `tradingagents/agents/`.
- §4.3 Structured outputs — Pydantic schemas in `tradingagents/schemas/outputs.py`; explain why JSON-string serialization is used.
- §4.4 Temporal cutoff — `effective_simulation_end_date_str` + `clamp_date_range_eod`; argue why this is non-trivial (vendor adapters, weekend execution, news without publish dates).
- §4.5 Anonymization — `TickerMapper`, deanonymization round-trip, `scrub_ticker_text`.
- §4.6 Execution model — `PaperLedger`, Zerodha fees, gross vs net (`backtest/metrics.py`).
- §4.7 **CBS metric (centerpiece).** Definition, derivation, instrumentation (per-node Langfuse latency), unit analysis. Tie back to ablation lattice.

**What to build:**
- [ ] Decide: CBS in its own subsection (§4.7) or promoted to its own §5 in the paper. **Recommendation: own §5** so it is visible in the table of contents and has space for a derivation block.
- [ ] Draft figure §3.2 first; all method prose follows the figure.

---

### 2.5 Experiments ❌
**What it is:** ~2.5 pages. Three core questions from `research-paper-writing/references/experiments.md`: better-than-baseline, ablation-attribution, generalization-under-stress.

**Outline:**
- Setup — tickers, periods, splits, LLM provider, seeds, cost model, B&H benchmark.
- Exp 1 (better-than-baseline) — full pipeline vs B&H across tickers × periods. Net total return, Sharpe, Sortino, max drawdown.
- Exp 2 (ablation-attribution) — `a1`/`a2`/`a3`/`full` lattice; net return delta and CBS per ablation.
- Exp 3 (CBS validation) — per-ablation CBS predicts which ablation wins on held-out periods; correlation plot.
- Exp 4 (memorization probe) — anonymization on/off; show that famous past dates lose part of their advantage when anonymized. (Supporting; trim if space-tight.)
- Exp 5 (rationale persistence) — fraction of runs where layer transitions agree (analyst → researcher → trader → judge); supports that CBS captures *real* coordination value, not noise.

**What to build:**
- [ ] Lock the ticker × period × seed grid in §4 of this file
- [ ] Decide which experiment is the headline plot and matches the abstract number

---

### 2.6 Conclusion ❌
**What it is:** ~⅓ page. Re-state the three contributions with one sentence each, headline number, and one honest limitation.

**What to build:**
- [ ] Single paragraph; no new claims

---

### 2.7 Limitations & Ethics ❌
**What it is:** Required for ML/Finance venues. Honest section, half a column.

**Working list of limitations:**
- Single-asset only; portfolio extension is future work.
- BM25 memory is not a learned retriever; the rationale chain may break under longer histories.
- CBS depends on per-node latency measurements that vary with provider load; we report mean ± std but not worst-case.
- Anonymization mitigates but does not eliminate memorization — the model still knows it is the Indian equity market.
- Backtest does not model true LOB dynamics; this is `ROADMAP.md` §4.1 future work.

**What to build:**
- [ ] Tie each limitation to a specific ablation or appendix table
- [ ] Ethics: discuss responsible-use language (no investment advice, retail-trader risk)

---

## Module 3 · Figures & Tables

### 3.1 Teaser figure ❌
**Goal:** Single-glance answer to "what is the paper about?". Two stacked panels: (top) raw alpha gain from single-agent → full pipeline; (bottom) the same gain after subtracting per-call latency × volatility (CBS). Top says "always go full"; bottom says "go full only above a regime-specific threshold".

**What to build:**
- [ ] Mock the figure on paper before computing real numbers
- [ ] Once experiments freeze, regenerate with real seed × ticker spread

---

### 3.2 System pipeline figure 🔶
**Current state:** `docs/dashboard.png` exists as a frontend screenshot. Not paper-quality and shows the live UI, not the engine graph.

**What to build:**
- [ ] Vector pipeline figure (LangGraph nodes from `graph/setup.py`, with the four ablation cuts shown as dotted lines that bypass nodes for `a1`/`a2`/`a3`)
- [ ] Caption that names every box and points at the corresponding `tradingagents/agents/` file in the supplement

---

### 3.3 CBS derivation figure ❌
**Goal:** One panel showing CBS = `latency × σ_per_sec + cost_bps`. X-axis: latency. Y-axis: required alpha to break even. Three curves for three volatility regimes. Mark each ablation's measured alpha as a horizontal line; the intersection is the regime where it wins.

**What to build:**
- [ ] Once `tradingagents/analytics/cbs_calculator.py` ships (ROADMAP §5.3), populate with real numbers

---

### 3.4 Equity curve panel 🔶
**Current state:** `scripts/backtest_ablation_analysis.ipynb` reads `results/{a1,a2,a3,full}_2024-05-01_2024-06-30_RELIANCE_NS.csv` and plots equity curves. One ticker, one window.

**What to build:**
- [ ] Multi-ticker, multi-period grid (4×4 or 5×3) of equity curves with B&H overlay
- [ ] Promote the notebook export path to a paper-quality function (PDF + 300 dpi PNG)

---

### 3.5 Core ablation table ❌
**Goal:** One table, one message. Rows = ablations. Columns = net return ↑, gross return ↑, Sharpe ↑, Sortino ↑, max drawdown ↓, mean per-decision latency ↓, CBS at median volatility, "wins on `n/N` periods". Bold the row CBS predicts as best.

**What to build:**
- [ ] booktabs style, no vertical lines, metric direction in headers
- [ ] One concise caption (setting + protocol; discussion in prose)

---

### 3.6 Rationale-persistence figure ❌
**Goal:** Sankey or stacked-bar: for each ablation, fraction of runs where each layer transition agrees (e.g. bull-stance → BUY-trader). Supports CBS by showing that coordination *content* — not just runtime — improves with depth.

**What to build:**
- [ ] Depends on `tradingagents/analytics/rationale_tracker.py` (ROADMAP §5.2). Hard blocker for this figure.

---

## Module 4 · Experiments to Run Before Submission

### 4.1 Ticker × period × seed grid ❌
**What it is:** The headline experiment matrix. Same grid drives Exp 1, 2, 3 in §2.5.

**Plan:**
- [ ] **Tickers (~5):** RELIANCE.NS (already done), HDFCBANK.NS, INFY.NS, TATAMOTORS.NS, SUNPHARMA.NS — covers banks, IT, auto, pharma, energy.
- [ ] **Periods (~3):** a low-vol period, a medium-vol period, and one stress period (e.g. earnings + macro shock window). Identify via NIFTY VIX before locking.
- [ ] **Seeds (≥3):** LLM is nondeterministic; report mean ± std on every metric.
- [ ] **Ablations (4):** `a1`, `a2`, `a3`, `full`.
- [ ] **Total runs:** ~5 × ~3 × ~3 × 4 ≈ **180 backtest runs**, each ~10–30 trading days. Cost-budget this against the LLM provider before launching.

**Risk register:**
- LLM rate limits — already centrally controlled by `tradingagents/llm_clients/llm_rate_limit.py`. Pre-warm a provider quota plan.
- Vendor quotas — yfinance is fine; Alpha Vantage/Kite have stricter caps. Decide vendor mix per category in `DEFAULT_CONFIG` before launching.
- Seed reproducibility — record provider, model, temperature, structured-output method, simulation cap policy in every run's `summary.json`.

---

### 4.2 CBS instrumentation run ❌
**What it is:** Re-run a subset of the grid with per-node latency capture turned on (Langfuse already records it). Output: mean and 95th-percentile latency per ablation per ticker. Used to populate Figure §3.3 and Table §3.5.

**Blocker:** `tradingagents/analytics/cbs_calculator.py` (ROADMAP §5.3) must ship first.

---

### 4.3 Anonymization on/off study ❌
**What it is:** Re-run a small subset (1 ticker × 1 period × 3 seeds) with `ENABLE_ANONYMIZATION` true and false. Compare returns and headline counts. If anonymization changes returns, that is evidence for memorization bias and supports contribution (3).

**Blocker:** Re-confirm `TickerMapper` round-trips correctly through every vendor adapter (ROADMAP §3.1 remaining work).

---

### 4.4 Rationale-persistence study ❌
**What it is:** Per-run extract the chain `analyst_signals → researcher_stance → trader_plan → risk_decision → final`. Score directional consistency. Used in Figure §3.6 and to argue *why* full pipeline beats `a1` on volatile periods.

**Blocker:** `tradingagents/analytics/rationale_tracker.py` (ROADMAP §5.2).

---

### 4.5 Negative-result / honesty experiment ❌
**What it is:** At least one regime where CBS predicts `a1` wins, and it does. Required for credibility — without it, reviewers will assume CBS is just a re-skin of "more agents is better".

**What to build:**
- [ ] Identify a low-volatility, high-cost regime (high spread / low volume), pre-register the prediction, then run.

---

## Module 5 · Claim-Evidence Map (Living Table)

> **Authoritative Phase 0+ table:** `docs/paper/claim-evidence-map.md` (rows R1–R7, contribution crosswalk).  
> The table below is a **short index**; keep both in sync when claims change.

| # | Claim | Evidence | Status |
|---|-------|----------|--------|
| R1 | Regime-dependent breakeven; shallow ablation can win below CBS. | Fig. 3.3, Table 3.5 | ❌ needs CBS code + grid |
| R2 | CBS predicts / ranks winning ablation on held-out periods. | Exp 3, Table 3.5 | ❌ needs CBS + split |
| R3 | Temporal cutoff matters vs uncapped baseline. | Appendix cap on/off | ❌ needs cap-off run |
| R4 | Anonymization probe (memorization). | Exp 4 / §4.3 | ❌ needs grid |
| R5 | Audit trail / structured stages. | Pipeline fig | 🔶 lattice + schemas exist |
| R6 | Multi-ticker × multi-regime generalization. | Main table | ❌ Phase 2 grid |
| R7 | Net vs gross under fees. | Table 3.5 | 🔶 `summary.json` (partial) |

**What to build:**
- [x] Initial map seeded (`docs/paper/claim-evidence-map.md`, 2026-04-29)
- [ ] Update at the end of each experiment week
- [ ] Strike any claim that is still ❌ at the abstract-freeze date

---

## Module 6 · Reviewer-Facing Self-Review

### 6.1 Five-dimension review checklist ❌
**What it is:** From `research-paper-writing/references/paper-review.md`. Run before camera-ready.

**Dimensions:**
- [ ] *Contribution* — is CBS sufficiently novel vs cost-aware routing in MoE inference?
- [ ] *Writing clarity* — every paragraph passes the topic-sentence-first test
- [ ] *Experimental strength* — multi-ticker × multi-period × multi-seed; appendix has full tables, not cherry picks
- [ ] *Evaluation completeness* — at least one negative/honest result; B&H baseline reported on every ticker
- [ ] *Method design soundness* — CBS derivation is unit-checked; latency measurement protocol is documented

---

### 6.2 Adversarial reading ❌
**What it is:** A red-team pass where a co-author argues the "Reject — incremental" position. Every objection must be either resolved in the paper or acknowledged in §2.7.

**Pre-loaded objections (resolve before submission):**
- *"CBS is just transaction-cost-vs-edge with extra steps."* — counter: latency × intraday σ has a different regime structure than fixed cost; show the regime crossover.
- *"Single-stock results don't generalize."* — counter: portfolio is future work, but multi-ticker × multi-regime grid spans the realistic single-asset use case.
- *"You only test on Indian equities."* — counter: replicate one US ticker for the appendix (e.g. AAPL in 2024-Q2) to show transfer.
- *"Anonymization is a fig leaf; the model still knows the market."* — counter: report effect size; do not over-claim.

---

## Phase Order

| Phase | Items | Rationale |
|-------|-------|-----------|
| **Phase 0 — Story lock** | §1.1, §1.2, §1.3, §5 (initial) — **done** (`docs/paper/`) | Cannot draft prose or run experiments without a locked claim list |
| **Phase 1 — Code blockers** | `ROADMAP.md` §5.3 CBS calculator, §5.2 rationale tracker, §3.1 anonymization vendor coverage, §4.2 cap test coverage | Hard prerequisites for Exp 2/3/4/5 |
| **Phase 2 — Experiment grid** | §4.1 ticker×period×seed, §4.2 CBS instrumentation, §4.3 anonymization, §4.4 rationale, §4.5 negative-result | Freeze data before drafting prose |
| **Phase 3 — Figures + tables** | §3.1, §3.2, §3.3, §3.4, §3.5, §3.6 | Figures drive section drafting per the skill |
| **Phase 4 — First end-to-end draft** | §2.4 Method → §2.5 Experiments → §2.2 Intro → §2.3 Related → §2.6 Conclusion → §2.7 Limitations → §2.1 Abstract | Skill recommends Method-first, Abstract-last |
| **Phase 5 — Reverse outline + adversarial review** | §6.1 checklist, §6.2 red-team, §5 final pass | Catch unsupported claims before submission |
| **Phase 6 — Camera-ready** | Polish, BibTeX, supplementary, code release tag | Standard final pass |

---

## File Map (paper artifacts)

> The paper artifacts live under `docs/paper/`. Manuscript itself can stay private until submission; the plan and review docs are tracked in-repo.

```
docs/
├── dashboard.png                # existing (kept; not used as paper figure)
└── paper/
    ├── outline.md               # paragraph-level outline per §2 (this file is the meta-plan)
    ├── claim-evidence-map.md    # living version of Module 5 table
    ├── self-review.md           # filled-in §6.1 checklist + §6.2 red-team
    ├── figures/
    │   ├── teaser.pdf           # §3.1
    │   ├── pipeline.pdf         # §3.2
    │   ├── cbs.pdf              # §3.3
    │   ├── equity_grid.pdf      # §3.4
    │   └── rationale.pdf        # §3.6
    ├── tables/
    │   └── core_ablation.tex    # §3.5 (booktabs)
    └── manuscript/              # LaTeX source — gitignored or private repo
```

**What to build:**
- [x] Create `docs/paper/` skeleton (Phase 0: `STORY_LOCK.md`, `claim-evidence-map.md`, `outline.md`, `bib-seed.bib`)
- [ ] Decide whether `manuscript/` is in this repo or a private companion repo before submission

---

## Cross-reference to `ROADMAP.md`

The paper plan above depends on the following code items from `ROADMAP.md`. Each is a **hard** blocker for at least one paper artifact.

| `ROADMAP.md` item | Status | Paper artifact that depends on it |
|---|---|---|
| §5.3 CBS calculator | ❌ | C1, C2, Figure 3.3, Table 3.5 last column, Exp 2/3 |
| §5.2 Explainable Stability Tracker (rationale chain) | ❌ | C5, Figure 3.6, Exp 5 |
| §3.1 Ticker mapping engine — full vendor coverage | 🔶 | C4, Exp 4 |
| §4.2 Temporal cap — broader tool clamp + integration tests | 🔶 | C3, Method §4.4, appendix cap-off ablation |
| §5.1 wire `buy_and_hold_total_return` into `summary.json` | 🔶 | All ticker-level B&H deltas in Table 3.5 |
| §4.3 advanced (size-based) slippage | 🔶 (optional) | Appendix robustness |
| §3.3 expand indicator catalog to ~60 | 🔶 (optional) | Not on critical path; cite as future work |
| §2.6 CRO veto gate | 🔶 (optional) | Not on critical path; cite as future work |

Code items not in the table above are **not** paper blockers; they should be deferred until after submission.

---

*Last updated: April 29, 2026.*
