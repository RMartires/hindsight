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

Two tickers, four windows, and N=1 is the main weakness. The full version of this phase (6 names, 5 seeds on every window, anonymization on and off) is about $700–900 of OpenRouter spend. The four frozen windows already cost about $26 on `qwen/qwen3.5-flash-02-23` (~7 cents per trading day, ~$6.50 per window). Scope below is smaller because of that cost. INFY is deferred. One TCS bull seed is done. Four more TCS bull seeds are pending, about **$18**. Anonymization-off is a later optional **$11**.

The finished seed used `qwen/qwen3.5-flash-02-23` with `LLM_STRUCTURED_OUTPUT_METHOD=json_mode`. The next four have to match that. `.env` is currently `qwen/qwen3.7-flash` and does not set the method, which falls back to `json_schema`. Do not rerun the four paid windows.

- [x] Extra seeds on TCS bull only (2024-06-03 .. 2024-09-03). **Runs finished: seeds 2–7, six extra trajectories, all 64 days, each in its own CSV.** RELIANCE stays a single trajectory. The TCS bear window is not in this count.
  - [x] Seed 2, finished 2026-09-30. `results/dates-TCS-june-2024-sept-2024-bull-seed2-jsonmode-dates.csv`. Net −1.85% (equity $98,148.65), max drawdown 6.12%, fees $351.32, signals 20 BUY / 31 HOLD / 13 SELL. Buy-and-hold +21.86% (alpha −23.71 pp). This is not the frozen Table 2 trajectory (+19.61%).
  - [x] Seeds 3–7 on disk, `results/dates-TCS-june-2024-sept-2024-bull-seed{3..7}-dates.csv`. End equity from the CSVs: seed 3 $108,228 (+8.23%), seed 4 $104,890 (+4.89%), seed 5 $105,146 (+5.15%), seed 6 $108,643 (+8.64%), seed 7 $112,020 (+12.02%). Not yet scored for MDD, fees, or signal counts.
- [ ] **Confirm seeds 3–7 used `qwen/qwen3.5-flash-02-23` with `LLM_STRUCTURED_OUTPUT_METHOD=json_mode`.** Their filenames lack the `jsonmode` tag that seed 2 carries. Check the run logs or the `llm` column before reporting them alongside seed 2 and the frozen run. If any used `qwen3.7-flash` or `json_schema`, exclude it and say so.
- [ ] **Score the seeds.** Net, gross, fee drag, MDD, B/H/S counts for seeds 2–7 with the same code path as Table 2. Report mean ± SD across the seven TCS bull trajectories (frozen + 6). The spread is wide (−1.85% to +19.61%); the paper has to state that plainly rather than lead with the frozen run.
- [ ] **Put the seeds in the paper.** Add a seed table or a row block to §4.4; change "N=1 per regime window" to "N=1 for three windows, N=7 for TCS bull" in §1 (*What this paper is not*), §4.1 table, §4.3 Table 1 "Stochasticity reported", §5 Limitations, and the Not-claimed block. Figure 1's TCS bull panel should either show all seven paths or say which one it shows.
- [ ] **INFY.NS deferred.** Both regimes, one seed, about $13, already in `regime-timeranges`. Add it only if a referee asks for a third name. Not in this round.
- [ ] Anonymization off on those same two TCS windows, one seed. About $11. One on/off table, not a full factorial.
- [x] Add a non-LLM baseline from prices already on disk. SMA crossover or a simple momentum rule. No model calls. Rule: 10/50 SMA state (long when the 10-day average is above the 50-day; flat otherwise), same ledger as Frozen E1 (`zerodha_delivery`, $100,000, zero slippage). Scored 2026-09-25 from Kite cache `tradingagents/dataflows/data_cache/market.duckdb` via `python scripts/rules_baseline.py`. Summary: `results/baselines/sma_summary.csv`. Net vs buy-and-hold: REL bear −1.29% vs −17.43% (alpha +16.14 pp); REL bull −4.43% vs +15.09% (alpha −19.51 pp); TCS bull +13.31% vs +21.86% (alpha −8.55 pp); TCS bear −4.07% vs −20.42% (alpha +16.35 pp).
- [ ] **Put the baseline in the paper.** It is scored but `main.tex` never mentions it. Add an "SMA 10/50" column to Table 2(a) (net return and alpha) or a short paragraph in §4.4, and one sentence in §4.5: the rule shows the same bear-window pattern (loses less than buy-and-hold) and a larger bull-window shortfall than the agent on both names, which supports reading the bear result as exposure management rather than LLM skill.
- [ ] Bootstrap confidence interval on the TCS seeds, and a paired comparison against the rules baseline. No model calls. Optional if time is short; without it the seeds are descriptive only.
- [ ] Reframe the contribution around what this budget can support: defensive coordination compresses drawdown and caps rally participation, with seed variance reported for TCS and a single trajectory for RELIANCE. INFY is out unless a referee asks. State that limit in the paper. Mostly Abstract, §1 *Case-study evaluation*, and §5 once the seeds and baseline are in.

## Phase 3 — Rewrite the manuscript (2–3 weeks, overlaps Phase 2)

- [x] Rewrite in your own voice. Manual pass done in `docs/overleaf/main.tex` (Oct 2026), then review-plan C1/C2: bold cut to leads and headers, “honest scoped” wording gone, duplicate Not-claimed block merged, templated contrasts trimmed, Intro case-study paragraph rewritten as a results preview. The *What this paper is / is not* paragraph leads are still there; keep or rename, your call.
- [ ] **Disclose AI-assisted writing in Acknowledgements.** Not in `main.tex` yet. Name the tools, say they were used for drafting and editing, and state that you verified the content and references. arXiv requires disclosure of significant text-to-text AI use; most journals now ask for it.
- [x] Move repo internals out of the article body. `PAPER_ABLATION` / `a1`–`a3`, S/M/E roadmap codes, and memory labels are out (review-plan B8). The regeneration script name in §4.6 and `regime-timeranges` in §4.1/§5 remain as `\texttt{}`; fine for a reproducibility paper.
- [x] Verify every citation by hand. Done 2026-10-12 against arXiv API / Crossref for all 13 entries (review-plan B0). Qian et al. was wrong (fake WWW 2026 DOI, wrong title, phantom author) and is now arXiv:2510.11695. Re-check only if any 2026 preprint gets a journal version before submission.
- [ ] Have one person with a finance or ML background read it before submission.
- [ ] **Decide on the anonymization-off run** (Phase 2, ~$11). §5 currently says “anonymization on but not ablated”. Either run it and add one on/off row, or leave the sentence.

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