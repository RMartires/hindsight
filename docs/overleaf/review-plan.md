# `main.tex` review plan

Review of `docs/overleaf/main.tex` (manual de-AI-voice pass, Oct 2026).
Work top to bottom: A blocks compilation, B is correctness, C is prose, D is cleanup.
Tick items off as they land on Overleaf.

## A. Compile / render breakers

- [x] **A1. §4.5 unwrapped math.** Pandoc's `\(...\)` became bare parentheses: `(K)`, `(F)`, `(F / (V\_0 \cdot K))`, `((K=83)`, `(F=\$635)`, `((9.53\%/108) days)`. `\cdot` outside math mode is a hard error. Replace with `$K$`, `$F$`, `$F/(V_0 \cdot K)$`, `$K=83$`, `$F=\$635$`, `$9.53\%/108$`.
- [x] **A2. Stray `\addlinespace` outside tables** in §4.2 (two blocks of three, around lines 414–416 and 430–432). Expands to `\noalign` and errors outside a tabular. Replace with `\medskip` or delete.
- [x] **A3. `\citet{Nguyen2026Toward}`** at lines 181 and 187 with `natbib` loaded but no `\bibliography`. Resolved the other way: all 13 references now live in `references.bib` (plainnat, author-year); every inline "Author (Year)" is a `\citet`/`\citep`/`\citealp`; the hand-typed References section is replaced by `\bibliography{references}`. Upload `references.bib` to the Overleaf project alongside `main.tex`.
- [x] **A4. Table 2 caption unterminated** (lines 544–546). Opening `(` never closed, no period after "risk-free rate". End it with `...risk-free rate).`
- [x] **A5. Unicode `α`** in §4.4 bullets and §4.5 is not available under pdfLaTeX + T1. Use `$\alpha$`. Also prefer `$\times$`, `$\rightarrow$`, `$\approx$`, `$-$` over `×`, `→`, `≈`, `−` throughout.
- [x] **A6. `\textbf{$\leq -10\%$}`** in the regime-rule table. `\textbf` does not bold math; use `$\leq -10\%$`.
- [x] **A7. §4.2 windows table** declared `{l l l X}` (4 columns) but rows have 3 cells. Change to `\begin{tabular}{@{} l l l @{}}` and drop `tabularx` there.
- [x] **A8. Stray `\noindent`** mid-paragraph at line 640. Remove.

## B. Factual and internal consistency

- [x] **B0. Reference verification.** All 13 entries checked against arXiv API / Crossref on 2026-10-12. 12 matched. **Qian et al.** was wrong: the WWW 2026 DOI `10.1145/3774904.3792821` does not resolve and no WWW record exists; real title is "...Trading **Benchmark** for LLM Agents" (not "Arena"); author list had a non-existent "Li, Z.". Now cited as arXiv:2510.11695 (2025), key `qian2025agent`; in-text year renders as 2025. Dewansh journal name corrected to "…Engineering, Management and Science", pages 58–64.
  - [ ] Propagate the Qian fix to `docs/paper/manuscript.md` (line 305), `docs/paper/submission/ios_manuscript.md` (line 208), and root `manuscript.tex` (lines 990–991), which still carry the bad DOI.

- [x] **B1. Anonymization: optional or mandatory?** Decision: mandatory (on in all reported runs). Table 3 "opt. anonymization" → "strict anonymization"; Conclusion "optional anonymization" → "mandatory ticker anonymization"; Contributions "optional anonymization" → "mandatory anonymization". §3.5 ("all LLM-facing prompts") and §4.1 ("Strict anonymization") already matched. Limitations bullet "anonymization on but not ablated" kept as is.
- [x] **B2. System name.** "Hindsight" everywhere; the single "Hindsight 20/20" in the Conclusion is replaced.
- [x] **B3. Title grammar.** Now "Hindsight Agent: A Multi-Agent System for Quantitative Trading"; label renamed to `\label{title}`.
- [x] **B4. Section numbering.** 3.5→3.4 (anonymization), 3.6→3.5 (metrics), 3.7→3.6 (observability). The only in-text cross-ref to the old §3.5 (Related Work, aliases sentence) now says §3.4. No references to old §3.6/§3.7 existed.
- [x] **B5. Table numbering by appearance.** Renumbered: qualitative comparison (§4.3) is now Table 1, agent vs buy-and-hold is Table 2, secondary risk metrics is Table 3, stance shares stays Table 4. All seven in-text mentions updated (§1, §3.5 metrics table, §4.3, §4.4 ×3, §4.5). Tables are hand-numbered text, no `\label`/`\ref`.
- [x] **B6. Table 4 preamble redundancy.** Dropped the note sentence; caption keeps "(% of trading days)".
- [x] **B7. `regime-timeranges`** now `\texttt{}` in §4.1 (the §5 mention already was).
- [x] **B8. Internal codes** removed from all five Contributions items (also dropped the trailing Pandoc `\\` on each item). Limitations bullet now describes the presets in words: "reduced-pipeline presets (market analyst only; all analysts without debate; debate without the risk stage) are implemented but not evaluated in §4" (mirrors `tradingagents/paper_ablation.py` a1/a2/a3).
- [ ] **B9. Multi-seed status.** `results/` now has TCS bull seeds 2–7. Paper says N=1 throughout. Fine for this draft, but update the Limitations bullet "no multi-seed variance" if those seeds ship.

## C. Prose

### C1. Typos and grammar

- [x] Abstract: "any llm bias" → "LLM"; "Hindsights full" → "Hindsight's"; "(two tickers × exogenous bear/bull labels. one deterministic…)" → semicolon; "The primary contribution is X, Y, and Z" → "contributions are".
- [x] Intro: `\textbf{What this paper is} \textbf{Hindsight} extends` — missing period after "is"; "Case-study evaluation We run" — needs period and bold lead to match siblings; "one bear and one bull calendar windows" → "window".
- [x] §2: "behaviors raising new demands" → "behaviors, raising"; "simulated trading feedback both comparators" → "feedback; both are comparators"; lowercase sentence start "we report a simplified…"; missing period after "replication stack"; "(§3.2) aligning" → "(§3.2), aligning"; BlindTrade sentence now `\citeauthor{}'s \textbf{BlindTrade} \citeyearpar{}` → "Jeon and Lee's BlindTrade (2026)". Also caught a line-wrapped "(Table 3)" in the "Empirical scope" paragraph that B5 missed; now "(Table 1)".
- [x] §3.3 comma-splice run-on rewritten as suggested.
- [x] §3.4: "e.g." moved outside `\texttt{}` (`e.g.\ \texttt{STOCK\_\#\#\#\#}`).
- [x] §3.6 Observability: "out" → fixed and expanded to four sentences: Langfuse via the LangChain callback handler, one trace per (ticker, trade date) with LLM calls / tool calls / tokens / latency, session-id keyed, complements §3.3 artifacts. Matches `tradingagents/observability/langfuse_config.py`.
- [x] §4.4: "stay defensive; downstream trader…".
- [x] §4.5: "fee levels, suggesting".
- [x] References: resolved by B0 — `references.bib` uses `B{\u{a}}dic{\u{a}}`, and in-text mentions are `\citet`, so both render "Bădică". The only literal "Bădică" left is in the Changelog table, which goes with D2.

### C2. AI-voice leftovers

- [x] **Bold density.** ~40 emphasis-only `\textbf{}` removed (all the listed ones plus tickers, "6.5% p.a.", "7.7/88 bps/day", "before/exogenously/independent", "differ by ticker", "no LOB claim", "agent architecture", "statistical stress tests", "auditability and temporal integrity", Conclusion result phrases, repeat mentions of TradingAgents/BlindTrade, fig names, `STOCK_####`). Kept: paragraph and item leads, table captions and row headers, §3.1 pipeline stage names, §3.5 primary-metric definitions, first mention of each named system in §2. "explainable stability" is now `\emph{}` (borrowed term).
- [x] **"honest"** gone: Intro → "a scoped, pre-specified regime-split case study"; Contributions → "Pre-specified regime-conditioned case study --- four windows fixed before any agent run, …".
- [x] **Duplicate "Not claimed:" block.** Kept the Conclusion one, merged in "multi-seed benchmarks; ablation results" from the Contributions copy, and deleted the latter.
- [x] **Templated framings.** Kept "articulate *what to measure* / implements *how to reproduce it*" (Positioning summary). Rewrote the other three plainly: §2 "the comparison there is qualitative, since the studies differ in seeds and universe breadth"; §4.1 "Section 4 describes how one stack behaves under contrasting underlying trends. It does not test a hypothesis about expected alpha…"; §4.5 "We read this as a regime-by-issuer interaction within one architecture."
- [x] **Intro "Case-study evaluation" paragraph** rewritten as a results preview instead of a setup repeat: \$100k per window, bear windows lose/draw down less, bull windows trail by 2.3 pp (TCS) and 9.5 pp (RELIANCE), pointer to §4 and §4.5. Numbers match Table 2 alphas.

## D. Structure and cleanup

- [x] **D1. §4.6 Figures.** Four PDFs copied to `docs/overleaf/figures/` and included as `figure` floats with captions and labels (`fig:equity-grid`, `fig:returns`, `fig:signals`, `fig:outlook-bullish`); bash block and bullets replaced by one sentence naming the regeneration script. **Upload the `figures/` folder to Overleaf with `main.tex` and `references.bib`.**
- [x] **D2. Changelog section** deleted (with its `longtable`/`minipage` block).
- [x] **D3. `\rule` separators** all removed (six, plus the commented one under the title).
- [x] **D4. Preamble** rewritten from 108 lines to ~35: dropped all `...Tok` macros, `Shaded`/`Highlighting`, `fancyvrb`, `color`, `longtable`, `calc`, `etoolbox` patch, `footnotehyper`/`footnote`, `\makesavenoteenv`, `\newcounter{none}`, `xmpquote` shim, `pdfcreator=pandoc`; added `graphicx` + `\graphicspath{{figures/}}` for D1. Kept `booktabs`, `array`, `tabularx`, `ragged2e`, `natbib`, `bookmark`/`hyperref`, `xurl`, `microtype`, `parskip`, `\tightlist`.
  - Verified with `tectonic` (installed via Homebrew, 2026-10-19): clean compile, 14 pages, 13 bib entries, no undefined refs/citations. Fixed three pre-existing overfull boxes along the way (§3.2 table columns narrowed to 2.2/3.3/3.3 cm; field-list and `resolve_ticker_for_vendor()` sentences reflowed). Remaining: one 0.6 pt overfull in a §3.2 table cell, invisible.
- [x] **D5. Title block.** Now `\title{}`/`\author{}`/`\maketitle` with the author block from `ios_manuscript.md` (Rohit Edward Martires, Independent researcher, Goa, India, email); `\date{}` left empty so no date prints. Abstract is a proper `abstract` environment. `pdftitle`/`pdfauthor` set in `hypersetup`. Compiles clean with `tectonic`. Swap `article` for the venue class when chosen; the title block will carry over.

## Order of work

1. A1–A8 (one compile pass, should go green).
2. B1–B4, B6, B7 (quick edits).
3. D2, D3, D4 (delete dead weight before prose pass so line numbers stabilise).
4. C1, then C2 (manual voice pass).
5. B5, B8, B9, D1, D5 (decisions, not fixes).
