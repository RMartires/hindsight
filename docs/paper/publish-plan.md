# Publish plan — Hindsight 20/20

**Goal:** publish the paper in a conventional journal, then use that DOI to appeal the arXiv decline.

**Last updated:** 2026-09-30.

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

- [ ] Extra seeds on TCS bull only (2024-06-03 .. 2024-09-03). **One seed done, four pending.** Report mean and standard deviation once those four finish. RELIANCE stays a single trajectory. The TCS bear window is not in this count. Write each seed to its own CSV. Do not overwrite the finished file or a frozen schedule.
  - [x] Seed 2, finished 2026-09-30. `results/dates-TCS-june-2024-sept-2024-bull-seed2-jsonmode-dates.csv`. 64 days. Net −1.85% (equity $98,148.65), max drawdown 6.12%, fees $351.32, signals 20 BUY / 31 HOLD / 13 SELL. Buy-and-hold +21.86% (alpha −23.71 pp). This is not the frozen Table 1 trajectory (+19.61%).
  - [ ] Seeds 3, 4, 5, and 6 pending.
- [ ] **INFY.NS deferred.** Both regimes, one seed, about $13, already in `regime-timeranges`. Add it only if a referee asks for a third name. Not in this round.
- [ ] Anonymization off on those same two TCS windows, one seed. About $11. One on/off table, not a full factorial.
- [x] Add a non-LLM baseline from prices already on disk. SMA crossover or a simple momentum rule. No model calls. Rule: 10/50 SMA state (long when the 10-day average is above the 50-day; flat otherwise), same ledger as Frozen E1 (`zerodha_delivery`, $100,000, zero slippage). Scored 2026-09-25 from Kite cache `tradingagents/dataflows/data_cache/market.duckdb` via `python scripts/rules_baseline.py`. Summary: `results/baselines/sma_summary.csv`. Net vs buy-and-hold: REL bear −1.29% vs −17.43% (alpha +16.14 pp); REL bull −4.43% vs +15.09% (alpha −19.51 pp); TCS bull +13.31% vs +21.86% (alpha −8.55 pp); TCS bear −4.07% vs −20.42% (alpha +16.35 pp).
- [ ] Bootstrap confidence interval on the TCS seeds, and a paired comparison against the rules baseline. No model calls.
- [ ] Reframe the contribution around what this budget can support: defensive coordination compresses drawdown and caps rally participation, with seed variance reported for TCS and a single trajectory for RELIANCE. INFY is out unless a referee asks. State that limit in the paper.

## Phase 3 — Rewrite the manuscript (2–3 weeks, overlaps Phase 2)

- [ ] Rewrite in your own voice. Keep the tables, numbers, and limitations. Remove template phrasing: “what this paper is / is not,” bold-keyword packing, “honest scoped case study,” stacked hedges.
- [ ] Disclose AI-assisted writing in Acknowledgements. Name the tools, say they were used for drafting and editing, and state that you verified the content and references. arXiv requires disclosure of significant text-to-text AI use; most journals now ask for it.
- [ ] Move repo internals out of the article body. `PAPER_ABLATION`, memory labels (`M3`, `M4`), `.cursor/memory.md` pointers, and CSV filenames belong in a supplementary README.
- [ ] Verify every citation by hand. Open each DOI and arXiv link. Confirm author list, year, title, and venue. Pay extra attention to 2026 preprints (Jeon and Lee, Miyazaki et al., Nguyen and Pham, Dewansh).
- [ ] Have one person with a finance or ML background read it before submission.

## Phase 4 — Venue and submission (about a week)

Pick one venue. Rough order of fit:

1. **Algorithmic Finance (SAGE).** CS × finance, Scopus and ESCI. Already the intended target, but the package still builds for IOS Press.
2. **PeerJ Computer Science.** Published a comparable LLM multi-agent trading paper in March 2026. Open review and reproducibility-friendly. Has an article processing charge.
3. **Journal of Financial Data Science** or **Quantitative Finance.** Higher bar, slower review, more scrutiny of the backtest.

- [ ] Confirm the chosen venue’s current guidelines, template, and fees.
- [ ] Retarget the build (`build_ios_package.sh`, `README_IOS.md`) and update `paper-roadmap.md` away from IOS Press.
- [ ] Tag a GitHub release and mirror it on Zenodo: frozen CSVs, seeds, prompts, the exact model string, and a one-command regeneration script.
- [ ] Write a short cover letter. Two sentences on the contribution, an honest scope statement, a pointer to the reproducibility package, and the AI-writing disclosure. Do not mention the arXiv decline.

## Phase 5 — After acceptance

- [ ] Add the journal reference and DOI, then appeal via the [arXiv support portal](https://info.arxiv.org/help/moderation/appeals.html). Include `MOD-103516`, `submit/7732697`, the accepted PDF, the DOI, and a short note on category fit (`q-fin.TR` or `q-fin.CP` primary, `cs.MA` cross-list).
- [ ] Update the Zenodo record to the published version and link both ways.
- [ ] Treat the next paper as journal-first too. The published-only restriction stays until arXiv says a significant number of articles have been published.