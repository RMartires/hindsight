# Publish plan — Hindsight 20/20

**Goal:** publish the paper in a conventional journal, then use that DOI to appeal the arXiv decline.

**Last updated:** 2026-09-23.

**arXiv status:** declined. Notice `MOD-103516` / `submit/7732697` (about two months after submission). Two separate decisions:

1. This manuscript was declined as “in need of significant review and revision” (stock language for not yet refereeable). No referee comments were given.
2. The account is now restricted: future submissions without a journal reference and a DOI that resolves to a journal site will be declined until there is a conventional publication record.

Do not resubmit this manuscript to arXiv as-is. Repeat uploads of declined work can freeze submission privileges.

**Venue note:** Algorithmic Finance transferred from IOS Press to SAGE, effective 2025-01-01. `README_IOS.md` and `build_ios_package.sh` still target the IOS format. Confirm SAGE’s current author guidelines and any APC before submitting.

---

## Phase 1 — Stop the bleeding (this week)

- [ ] Do not resubmit to arXiv. Not the same PDF, not a light revision.
- [ ] Do not appeal yet. An appeal without a journal DOI will be denied on the account restriction alone.
- [ ] Upload the current PDF to Zenodo for a free priority timestamp and DOI. This does not satisfy arXiv’s journal-ref requirement.
- [ ] Archive `MOD-103516` and `submit/7732697` somewhere private (not in `docs/paper/`). You will need them for the later appeal.

## Phase 2 — Fix what a referee will reject (4–8 weeks)

Two tickers, four windows, and N=1 is the main weakness. Address it before submitting anywhere.

- [ ] Widen the universe. Run Infosys (already in `regime-timeranges`, never run) plus 2–3 more NSE large-caps. Target 5–6 names.
- [ ] Multi-seed. At least 5 runs per window with LLM temperature above 0. Report mean and standard deviation. Comparators report 20–50 seeds; matching that is not required, but N=1 cannot stand.
- [ ] Ablate anonymization. On/off on the same windows, one table. The stack implements it and cites BlindTrade, then does not test it.
- [ ] Add a non-LLM baseline. Buy-and-hold alone is not enough. Add at least one rules-based strategy (SMA crossover or a simple momentum rule).
- [ ] Add a statistical test. Bootstrap confidence interval on alpha across seeds, or a paired test of agent vs baseline per window.
- [ ] Reframe the contribution. Lead with a finding (defensive coordination compresses drawdown and caps rally participation, checked across names and seeds). Present the stack as the instrument that made the finding auditable.

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
