# Publish plan — Hindsight

**Goal:** publish the paper in a conventional journal, then use that DOI to appeal the arXiv decline.

**Last updated:** 2026-10-19. Manuscript source of truth is now `docs/overleaf/` (`main.tex`, `references.bib`, `figures/`), mirrored on Overleaf and compiling clean. The LaTeX/prose pass is tracked in `docs/overleaf/review-plan.md` (all items done except the two noted under Housekeeping below). `docs/paper/manuscript.md`, `docs/paper/submission/ios_manuscript.md`, and root `manuscript.tex` are stale copies.

**arXiv status:** declined. Notice `MOD-103516` / `submit/7732697` (about two months after submission). Two separate decisions:

1. This manuscript was declined as “in need of significant review and revision” (stock language for not yet refereeable). No referee comments were given.
2. The account is now restricted: future submissions without a journal reference and a DOI that resolves to a journal site will be declined until there is a conventional publication record.

Do not resubmit this manuscript to arXiv as-is. Repeat uploads of declined work can freeze submission privileges.

**Venue note:** Algorithmic Finance transferred from IOS Press to SAGE, effective 2025-01-01. `README_IOS.md` and `build_ios_package.sh` still target the IOS format. Confirm SAGE’s current author guidelines and any APC before submitting.

---

## Phase 1 — Stop the bleeding (this week)

- [x] Do not resubmit to arXiv. Not the same PDF, not a light revision.
- [x] Do not appeal yet. An appeal without a journal DOI will be denied on the account restriction alone.
- [x] Archive `MOD-103516` and `submit/7732697` somewhere private (not in `docs/paper/`). You will need them for the later appeal.

## Phase 2 — Fix what a referee will reject (4–8 weeks)

Two tickers, four windows, and N=1 is the main weakness. The full version of this phase (6 names, 5 seeds on every window, anonymization on and off) is about $700–900 of OpenRouter spend. The four frozen windows already cost about $26 on `qwen/qwen3.5-flash-02-23` (~7 cents per trading day, ~$6.50 per window). Scope below is smaller because of that cost. INFY is deferred. TCS bull seeds 2–7 are on disk. Anonymization-off is a later optional **$11**. Do not rerun the paid windows.

- [x] Extra seeds on TCS bull only (2024-06-03 .. 2024-09-03). **Runs finished: seeds 2–7, six extra trajectories, all 64 days, each in its own CSV.** RELIANCE stays a single trajectory. The TCS bear window is not in this count.
  - [x] Seed 2, finished 2026-09-30. `results/dates-TCS-june-2024-sept-2024-bull-seed2-jsonmode-dates.csv`. Net −1.85% (equity $98,148.65), max drawdown 6.12%, fees $351.32, signals 20 BUY / 31 HOLD / 13 SELL. Buy-and-hold +21.86% (alpha −23.71 pp). This is not the frozen Table 2 trajectory (+19.61%).
  - [x] Seeds 3–7 scored 2026-10-20 from daily `equity`, `close`, `cumulative_fees`, and `final_signal` ($100,000 start; 64 days, 2024-06-03 .. 2024-09-03). Buy-and-hold is +21.86% on every file (close 3702.85 → 4512.35), the same figure as Table 2. Stored `total_return` matched this recompute; stored `max_drawdown` matched too (it did not for seed 2).

    | Seed | Net | Gross | Fee drag | Fees | Alpha | MDD | B/H/S |
    |---|---:|---:|---:|---:|---:|---:|---|
    | 3 | +8.23% | +9.71% | 1.48 pp | $1,483 | −13.63 pp | 2.68% | 8/43/13 |
    | 4 | +4.89% | +5.60% | 0.72 pp | $715 | −16.97 pp | 3.11% | 4/39/21 |
    | 5 | +5.15% | +6.98% | 1.83 pp | $1,834 | −16.72 pp | 1.81% | 11/41/12 |
    | 6 | +8.64% | +10.28% | 1.64 pp | $1,635 | −13.22 pp | 1.42% | 11/33/20 |
    | 7 | +12.02% | +12.89% | 0.87 pp | $871 | −9.84 pp | 2.74% | 8/41/15 |

    Seeds 3–7 only: net +7.79% ± 2.92, alpha −14.08 ± 2.92 pp, MDD 2.35% ± 0.70. Every one trails buy-and-hold.
- [x] **Model for seeds 3–7 confirmed** (author, 2026-10-19): `qwen/qwen3.5-flash-02-23` throughout, same as the frozen windows and seed 2. That is the only model string the paper reports (`main.tex` §2 and §5). No method footnote: the paper does not name `json_mode` or `json_schema`. The schedule CSVs do not record the LLM, so this rests on the author's record.
- [x] **Score the seeds.** Seeds 2–7 recomputed from the daily series (seed 2 confirmed at −1.85% net, 6.12% MDD, $351 fees, 20/31/13). Frozen TCS bull is the published Table 2 row (+19.61% net, 1.65% MDD, $2,198 fees, 13/14/40); its CSV is not on disk, so that point was not recomputed. Across the seven: net **+8.10% ± 6.66**, alpha **−13.76 ± 6.66 pp**, MDD **2.79% ± 1.60**. Range of net return is −1.85% to +19.61%. The frozen run is the best of the seven, not the typical one. Seeds have 64 rows; Table 2 says 67 days for the frozen window. Endpoints match, so buy-and-hold is the same +21.86%.
- [x] **Put the seeds in the paper** (2026-10-20). Table 3 is seeds 3–7 only (N=5). The frozen Table 2 run is not in that mean. Seed 2 is scored above and left out. Across the five: net **+7.79% ± 2.92**, alpha **−14.08 ± 2.93 pp**, MDD **2.35% ± 0.71**. Prose contrasts the frozen −2.3 pp with the five-run mean of −14.1 pp. Old Tables 3 and 4 are now 4 and 5. §4.6 states that each TCS bull panel is the frozen trajectory, not the five-run mean.
- [x] **INFY.NS not in the paper** (author, 2026-10-20). No INFY run was done, so no third ticker is added. The Limitations sentence that said Infosys windows were planned but not run has been removed.
- [x] **No anonymization-off run.** Anonymization was on for every reported run. The off condition (~$11) is not being added. §5 now says “ticker anonymization on for every reported run” and no longer lists an anonymization ablation as future work.
- [x] Add a non-LLM baseline from prices already on disk. SMA crossover or a simple momentum rule. No model calls. Rule: 10/50 SMA state (long when the 10-day average is above the 50-day; flat otherwise), same ledger as Frozen E1 (`zerodha_delivery`, $100,000, zero slippage). Scored 2026-09-25 from Kite cache `tradingagents/dataflows/data_cache/market.duckdb` via `python scripts/rules_baseline.py`. Summary: `results/baselines/sma_summary.csv`. Net vs buy-and-hold: REL bear −1.29% vs −17.43% (alpha +16.14 pp); REL bull −4.43% vs +15.09% (alpha −19.51 pp); TCS bull +13.31% vs +21.86% (alpha −8.55 pp); TCS bear −4.07% vs −20.42% (alpha +16.35 pp).
- [x] **Put the baseline in the paper** (2026-10-20). New Table 3: 10/50 SMA net and alpha next to the Table 2 agent. Bear windows: the rule also loses less than buy-and-hold, and by more than the agent. Bull windows: the rule trails on both names; the frozen TCS agent beats it, the five repeat runs (mean +7.79%) do not. §4.5 notes the bear pattern is not specific to the agent. Seed table is now Table 4, secondary metrics Table 5, outlook Table 6.
- [ ] Bootstrap confidence interval on the TCS seeds, and a paired comparison against the rules baseline. No model calls. Optional if time is short; without it the seeds are descriptive only.
- [ ] Reframe the contribution around what this budget can support: defensive coordination compresses drawdown and caps rally participation, with seed variance reported for TCS bull (five runs) and a single trajectory for the other three windows. INFY is not in this paper. Mostly Abstract, §1 *Case-study evaluation*, and §5 once the baseline is in.

## Phase 3 — Rewrite the manuscript (2–3 weeks, overlaps Phase 2)

- [x] Rewrite in your own voice. Manual pass done in `docs/overleaf/main.tex` (Oct 2026), then review-plan C1/C2: bold cut to leads and headers, “honest scoped” wording gone, duplicate Not-claimed block merged, templated contrasts trimmed, Intro case-study paragraph rewritten as a results preview. The *What this paper is / is not* paragraph leads are still there; keep or rename, your call.
- [ ] **Disclose AI-assisted writing in Acknowledgements.** Not in `main.tex` yet. Name the tools, say they were used for drafting and editing, and state that you verified the content and references. arXiv requires disclosure of significant text-to-text AI use; most journals now ask for it.
- [x] Move repo internals out of the article body. `PAPER_ABLATION` / `a1`–`a3`, S/M/E roadmap codes, and memory labels are out (review-plan B8). The regeneration script name in §4.6 and `regime-timeranges` in §4.1/§5 remain as `\texttt{}`; fine for a reproducibility paper.
- [x] Verify every citation by hand. Done 2026-10-12 against arXiv API / Crossref for all 13 entries (review-plan B0). Qian et al. was wrong (fake WWW 2026 DOI, wrong title, phantom author) and is now arXiv:2510.11695. Re-check only if any 2026 preprint gets a journal version before submission.
- [ ] Have one person with a finance or ML background read it before submission.
- [x] **Anonymization-off run declined.** Same decision as Phase 2: anonymization stayed on for every run, and the paper does not promise an off condition.

## Phase 4 — Venue and submission (about a week)

Pick one venue. Rough order of fit:

1. **Algorithmic Finance (SAGE).** CS × finance, Scopus and ESCI. Already the intended target, but the package still builds for IOS Press.
2. **PeerJ Computer Science.** Published a comparable LLM multi-agent trading paper in March 2026. Open review and reproducibility-friendly. Has an article processing charge.
3. **Journal of Financial Data Science** or **Quantitative Finance.** Higher bar, slower review, more scrutiny of the backtest.

- [ ] Confirm the chosen venue’s current guidelines, template, and fees.
- [ ] **Swap the document class.** `main.tex` is plain `article` with `\title`/`\author`/`\maketitle`, `natbib` + `plainnat`, `booktabs`/`tabularx`, `graphicx`. Replace the class and bib style with the venue template; the body should carry over. Hand-numbered headings (`\subsection{1. Introduction}` with `secnumdepth=-\maxdimen`) will need to become normal `\section`s if the template numbers automatically.
- [ ] Retarget or retire the IOS package (`build_ios_package.sh`, `README_IOS.md`, `ios_manuscript.md`) and update `paper-roadmap.md` away from IOS Press. The Overleaf tree is the live source; do not maintain two.
- [ ] Tag a GitHub release and mirror it on Zenodo: frozen CSVs, the six TCS bull seed CSVs, baseline CSVs, prompts, the exact model string and structured-output method, and a one-command regeneration script. Cite the Zenodo DOI from the *Code and artifacts* line in the abstract.
- [ ] Write a short cover letter. Two sentences on the contribution, an honest scope statement, a pointer to the reproducibility package, and the AI-writing disclosure. Do not mention the arXiv decline.

## Housekeeping (any time before submission)

- [ ] Commit `docs/overleaf/main.tex` and `review-plan.md` (currently modified, uncommitted). `docs/overleaf/figures/` is gitignored by the `*figures*` rule at `.gitignore:49`; add `!docs/overleaf/figures/` if the PDFs should be tracked, otherwise regenerate them from `scripts/generate_paper_figures.py` on checkout.
- [ ] Propagate the Qian citation fix to `docs/paper/manuscript.md` (line 305), `docs/paper/submission/ios_manuscript.md` (line 208), and root `manuscript.tex` (lines 990–991), or delete those copies once the IOS package is retired (review-plan B0 sub-item).
- [ ] Close review-plan B9 once the seeds are in the paper.
- [ ] Keep `tectonic main.tex` (installed via Homebrew 2026-10-19) as the local check before each Overleaf upload: expect 0 errors, 0 undefined citations, one 0.6 pt overfull in the §3.2 table.

## Minimum path to a submittable PDF

If time is the constraint, these are the items a desk editor or referee will notice are missing; the rest raise the odds but do not block: confirm and score seeds 3–7 → seeds into §4.4 and the N=1 statements → baseline into Table 2 → AI disclosure → venue template → Zenodo release → cover letter.

## Phase 5 — After acceptance

- [ ] Add the journal reference and DOI, then appeal via the [arXiv support portal](https://info.arxiv.org/help/moderation/appeals.html). Include `MOD-103516`, `submit/7732697`, the accepted PDF, the DOI, and a short note on category fit (`q-fin.TR` or `q-fin.CP` primary, `cs.MA` cross-list).
- [ ] Update the Zenodo record to the published version and link both ways.
- [ ] Treat the next paper as journal-first too. The published-only restriction stays until arXiv says a significant number of articles have been published.