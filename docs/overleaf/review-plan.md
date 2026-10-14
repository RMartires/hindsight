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

- [ ] Abstract: "any llm bias" → "LLM"; "Hindsights full" → "Hindsight's"; "(two tickers × exogenous bear/bull labels. one deterministic…)" → semicolon; "The primary contribution is X, Y, and Z" → "contributions are".
- [ ] Intro: `\textbf{What this paper is} \textbf{Hindsight} extends` — missing period after "is"; "Case-study evaluation We run" — needs period and bold lead to match siblings; "one bear and one bull calendar windows" → "window".
- [ ] §2: "behaviors raising new demands" → "behaviors, raising"; "simulated trading feedback both comparators" → "feedback; both are comparators"; lowercase sentence start "we report a simplified…" (line 181); missing period after "replication stack" (line 195); "(§3.2) aligning" → "(§3.2), aligning"; "Jeon and Lee (2026) (\textbf{BlindTrade})" → "Jeon and Lee's BlindTrade (2026)".
- [ ] §3.3 comma-splice run-on. Suggested: "Analyst tool calls respect the simulation end date: vendor queries are clamped so no data after the as-of trade date is returned. Each stage emits a Pydantic-validated object, giving typed JSON artifacts."
- [ ] §3.5: move "e.g." outside `\texttt{}` in `(\texttt{e.g. STOCK\_\#\#\#\#})`.
- [ ] §3.7: "into out TradingAgent" → "our". Expand to say what is traced (per-stage LLM calls, tool calls, tokens/cost per trading day) or fold into §3.3.
- [ ] §4.4: "stay defensive downstream trader and risk stages drive" — restore separator: "stay defensive; downstream trader…".
- [ ] §4.5: "fee levels suggesting" → "fee levels, suggesting".
- [ ] References: "Badica" (refs) vs "Bădică" (text). Make consistent.

### C2. AI-voice leftovers

- [ ] **Bold density.** Nearly every noun phrase is `\textbf{}`. Keep bold for paragraph leads and first use of a defined term. Unbold: "loses less", "markedly lower MDD", "SELL-heavy", "noisy", "not", "N=1", "\$100,000", "compress drawdown", "cap rally participation", "nearly track".
- [ ] **"honest"** appears twice ("honest, scoped regime-split case study"; "Honest regime-conditioned case study"). Replace with "scoped" / "pre-specified".
- [ ] **Duplicate "Not claimed:" block** in Conclusion and Contributions. Keep one.
- [ ] **Templated framings**, trim to one: "articulate *what to measure*, Hindsight implements *how to reproduce it*"; "complementary, not directly comparable"; "not a universal win/loss verdict"; "illustrative stress test".
- [ ] **Intro "Case-study evaluation" paragraph** repeats the abstract nearly verbatim. Cut or rewrite.

## D. Structure and cleanup

- [ ] **D1. §4.6 Figures** has a bash command and filename bullets, no figures. Either `\includegraphics` the four PDFs (see `docs/paper/submission/ios_manuscript.md` for the block) or delete the section.
- [ ] **D2. Changelog section** should not ship; it is also the last `longtable`/`minipage` block. Delete.
- [ ] **D3. `\begin{center}\rule{0.5\linewidth}{0.5pt}\end{center}`** separators are Markdown `---` artifacts. Remove all.
- [ ] **D4. Preamble.** After D2, drop the ~40 syntax-highlighting `\newcommand{...Tok}` macros, `longtable`, `calc`, `footnotehyper`/`footnote`, `\makesavenoteenv`, `\newcounter{none}`, and the `\patchcmd\longtable` block. Keep `booktabs`, `array`, `tabularx`, `ragged2e`, `hyperref`/`bookmark`.
- [ ] **D5. Title block.** `\author{}`/`\date{}` are empty and there is no `\maketitle`; title is a `\section`. OK for draft; swap to `\title`/`\author`/`\maketitle` when a venue template is chosen.

## Order of work

1. A1–A8 (one compile pass, should go green).
2. B1–B4, B6, B7 (quick edits).
3. D2, D3, D4 (delete dead weight before prose pass so line numbers stabilise).
4. C1, then C2 (manual voice pass).
5. B5, B8, B9, D1, D5 (decisions, not fixes).
