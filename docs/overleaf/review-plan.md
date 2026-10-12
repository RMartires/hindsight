# `main.tex` review plan

Review of `docs/overleaf/main.tex` (manual de-AI-voice pass, Oct 2026).
Work top to bottom: A blocks compilation, B is correctness, C is prose, D is cleanup.
Tick items off as they land on Overleaf.

## A. Compile / render breakers

- [ ] **A1. §4.5 unwrapped math.** Pandoc's `\(...\)` became bare parentheses: `(K)`, `(F)`, `(F / (V\_0 \cdot K))`, `((K=83)`, `(F=\$635)`, `((9.53\%/108) days)`. `\cdot` outside math mode is a hard error. Replace with `$K$`, `$F$`, `$F/(V_0 \cdot K)$`, `$K=83$`, `$F=\$635$`, `$9.53\%/108$`.
- [ ] **A2. Stray `\addlinespace` outside tables** in §4.2 (two blocks of three, around lines 414–416 and 430–432). Expands to `\noalign` and errors outside a tabular. Replace with `\medskip` or delete.
- [ ] **A3. `\citet{Nguyen2026Toward}`** at lines 181 and 187 with `natbib` loaded but no `\bibliography`. Prints `(?)`. Change both to inline "Nguyen and Pham (2026)" to match the rest of the paper, then drop `\usepackage{natbib}`.
- [ ] **A4. Table 2 caption unterminated** (lines 544–546). Opening `(` never closed, no period after "risk-free rate". End it with `...risk-free rate).`
- [ ] **A5. Unicode `α`** in §4.4 bullets and §4.5 is not available under pdfLaTeX + T1. Use `$\alpha$`. Also prefer `$\times$`, `$\rightarrow$`, `$\approx$`, `$-$` over `×`, `→`, `≈`, `−` throughout.
- [ ] **A6. `\textbf{$\leq -10\%$}`** in the regime-rule table. `\textbf` does not bold math; use `$\leq -10\%$`.
- [ ] **A7. §4.2 windows table** declared `{l l l X}` (4 columns) but rows have 3 cells. Change to `\begin{tabular}{@{} l l l @{}}` and drop `tabularx` there.
- [ ] **A8. Stray `\noindent`** mid-paragraph at line 640. Remove.

## B. Factual and internal consistency

- [ ] **B1. Anonymization: optional or mandatory?** §3.5 says it is applied to "all LLM-facing prompts"; code has a flag (`enable_anonymization`, default off in `tradingagents/default_config.py`, defaulted on by `scripts/backtest_mvp.py`). §4.1 says "Strict anonymization", Table 3 says "opt. anonymization", Conclusion says "optional anonymization". Use one framing everywhere: "optional; enabled in all four reported runs".
- [ ] **B2. System name.** Title/abstract/intro say "Hindsight"; Conclusion says "Hindsight 20/20". Pick one.
- [ ] **B3. Title grammar.** "A Multi-Agent for Quantitative Trading System" → "A Multi-Agent System for Quantitative Trading". Remove leftover `\label{manuscript-draft-export-to-pdf-latex}`.
- [ ] **B4. Section numbering.** §3.3 jumps to §3.5 (no 3.4), then 3.6, 3.7. Renumber 3.1–3.6.
- [ ] **B5. Table numbering by appearance.** Table 3 (§4.3) appears before Table 1 (§4.4); Table 4 follows Table 2. Renumber in order of appearance or accept and note it.
- [ ] **B6. Table 4 preamble redundancy.** Caption says "(% of trading days)" and the note repeats "Shares are percent of trading days." Drop one.
- [ ] **B7. `regime-timeranges`** in §4.1 is a file; use `\texttt{}` not `\textbf{}`.
- [ ] **B8. Internal codes** in Contributions ("S5 / M6", "S4 / M4--M5", "S2 / E1") and `a1`–`a3` presets in Limitations mean nothing to a reader. Remove or explain in one sentence.
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
