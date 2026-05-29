---
title: "Point-in-Time Multi-Agent LLM Trading: A Reproducible LangGraph Stack with Regime-Conditioned Case Study Evaluation and Fair Backtesting"
date: 29 May 2026
geometry: margin=1in
fontsize: 12pt
documentclass: article
numbersections: true
abstract: |
  Published LLM trading stacks are often hard to reproduce, rarely enforce temporal data boundaries, and seldom report net returns after fees. We present **Hindsight 20/20**, an open **LangGraph** stack with structured **Pydantic** outputs, point-in-time data access, optional **ticker anonymization**, and a fee-aware **paper backtest**. The primary contribution is reproducible systems engineering with frozen CSV artifacts---not a universe-scale alpha benchmark. As an illustrative case study, we evaluate the **full** pipeline on **RELIANCE.NS** and **TCS.NS** in **four pre-specified regime windows** (two tickers $\times$ exogenous bear/bull labels; **one trajectory per window**, no seed averaging). In both bear windows, the agent loses less than buy-and-hold with lower drawdown; bull outcomes diverge (RELIANCE lags B\&H; TCS nearly tracks it). Heterogeneous bull outcomes are consistent with a structurally defensive posture; whether this reflects coordinated de-risking or reduced equity exposure is underdetermined at N=1. Code: https://github.com/RMartires/hindsight
header-includes:
  - \usepackage{setspace}
  - \doublespacing
  - \usepackage{graphicx}
  - \usepackage{amsmath}
  - \usepackage{booktabs}
  - \usepackage{float}
  - \usepackage{xcolor}
  - \newcommand{\agentpct}[1]{\mbox{\textcolor{blue}{#1}\%}}
  - \AtBeginDocument{\author{Rohit Edward Martires\\Independent researcher, Goa, India\\\texttt{rohitmartires14@gmail.com}}}
---

**Keywords:** algorithmic trading; large language models; multi-agent systems; reproducibility; point-in-time data; market regimes.

## Introduction

Researchers are experimenting with LLMs inside trading workflows amid rapid growth in LLM-driven agent systems (B\u{a}dic\u{a} et al., 2025), but rarely report how the **same stack** behaves across **different underlying trends**, enforce point-in-time data at the adapter layer, or report **net** returns after stated fees.

**What this paper is.** **Hindsight 20/20** extends **TradingAgents** (Xiao et al., 2024) with schema-constrained outputs, a simulation end date, optional ticker anonymization, and a scriptable fee-aware backtest tied to **frozen CSV artifacts**.

**What this paper is not.** We do **not** claim state-of-the-art risk-adjusted returns, regime prediction, or generalization from a broad universe. Each regime window is **N=1** (no multi-seed variance). Frontier benchmarks (Jeon and Lee, 2026; Miyazaki et al., 2026) average many seeds across index universes; our scope is narrower and labeled as such (Section 4.1).

We evaluate the **full** pipeline on **RELIANCE.NS** and **TCS.NS** in **four pre-specified regime windows** (bear and bull per ticker), each from \$100,000 paper cash.

## Related Work

**LLM agents and classic MAS.** Multi-agent trading frameworks orchestrate specialist roles (Xiao et al., 2024; Yu et al., 2023; Yang et al., 2023). B\u{a}dic\u{a} et al.\ (2025) contrast emergent LLM agents with classic BDI multi-agent systems. **TradingAgents** supplies our graph skeleton; **AlphaAgents** (Zhao et al., 2025) validates institution-style role separation; **QuantAgents** (Li et al., 2025) emphasizes manager-led meetings---comparators for our debate loop, but neither foregrounds adapter-level point-in-time routing or frozen schedule CSVs.

**Methodological standards and bias control.** Nguyen and Pham (2026) propose Consolidated Minimum Standards for LLM financial multi-agent evaluation---contamination control, net-of-cost returns, and regime awareness---and introduce the Coordination Breakeven Spread (CBS). Bailey et al.\ (2014) warn that undisclosed configuration search makes strong backtests easy to overfit; we respond with pre-specified windows and frozen artifacts. While TradingAgents provides the foundational graph, Hindsight 20/20 implements the point-in-time policy and net-cost ledger those standards recommend.

**Anonymization and fine-grained tasks.** Jeon and Lee (2026) (*BlindTrade*) show that identifiers such as \texttt{AAPL} can trigger memorized pretraining rather than active reasoning; they anonymize S\&P~500 names and report Sharpe 1.40\,$\pm$\,0.22 across 20 seeds. Hindsight's optional \texttt{STOCK\_\#\#\#\#} aliases pursue the same goal in a LangGraph replication stack. Miyazaki et al.\ (2026) prove fine-grained analyst sub-tasks outperform coarse prompts; our analysts are tool-bound to indicators and statements (Section~3.2). Dewansh (2026) defines \emph{explainable stability} and rationale persistence; our Pydantic stage outputs support audit trails from outlook to \texttt{final\_signal}.

**Benchmarks and simulation realism.** Qian et al.\ (2026) (*Agent Market Arena*) show agent architecture often matters more than LLM backbone---motivating our fixed-model, regime-varying case study. Papadakis et al.\ (2025) (*StockSim*) define order-level simulation with latency and slippage; our candlestick ledger with stated fees is deliberately simpler, with StockSim-class realism as future work.

**Scope contrast.** Jeon and Lee (2026), Li et al.\ (2025), and Miyazaki et al.\ (2026) stress multi-seed index evaluation; Hindsight stresses reproducible temporal integrity on four pre-specified windows (Table 2).

## Method / System

**TradingAgentsGraph**: analysts $\to$ bull/bear debate $\to$ trader $\to$ risk. Section 4 uses **`PAPER_ABLATION=full`**. **`backtest_mvp.py --dates-csv`** produces wide schedule CSVs.

### Analyst task decomposition

| Stage | Tools | Tasks |
|-------|-------|-------|
| Market | `get_stock_data`, `get_indicators` | OHLCV + up to 8 Tier-1 indicators (SMA, EMA, MACD, RSI, Bollinger, ATR, VWMA, MFI) |
| Fundamentals | `get_fundamentals`, statements | Revenue, margins, balance-sheet trends |
| News / Sentiment | `get_news`, `get_global_news` | Company and macro news synthesis |
| Debate $\to$ Risk | --- | Structured stances $\to$ **BUY/HOLD/SELL** |

### Ticker anonymization

Deterministic \texttt{STOCK\_\#\#\#\#} aliases for LLM I/O; vendor round-trip de-anonymization; news proper-noun scrubbing. Frozen E1: \texttt{enable\_anonymization=True}.

### Backtest metrics

We emphasize **net return**, **MDD**, **fee drag**, and **alpha vs buy-and-hold**. **Excess Sharpe** uses daily equity from frozen CSVs with a **6.5\% p.a.** risk-free rate (India short-rate proxy)\footnote{Annualization: $\sqrt{252}$; NSE $\approx$240--250 trading days.}. Sortino and Calmar are secondary on short windows (67--111 days).

## Case Study Evaluation

### Scope and limits (Section 4.1)

Two liquid NSE large-caps; **four regime windows**; **N=1 trajectory per window**; exogenous bear/bull labels ($\pm$10\% underlying B\&H); pre-specified calendars in **`regime-timeranges`**. Not a hypothesis test about expected alpha.

### Positioning (Table 2)

\scriptsize
\begin{table}[htbp]
\centering
\setlength{\tabcolsep}{2pt}
\begin{tabular}{@{} l c c c c @{}}
\toprule
 & Hindsight & BlindTrade & QuantAgents & Expert Teams \\
\midrule
Primary goal & PIT reproducibility & Anonymized policy & Meetings & Hierarchy \\
Seeds & N=1/window & 20 & Multi-year & 50 \\
Universe & 2 NSE names & S\&P 500 & Simulation & TOPIX 100 \\
Costs & Net (Zerodha) & Varies & Varies & Varies \\
\bottomrule
\end{tabular}
\caption{Qualitative comparison; Hindsight is not comparable on seeds/universe.}
\end{table}
\normalsize

### Results

**Table 3.** Primary metrics from frozen CSVs (\$100,000 start).

\begin{table}[htbp]
\centering
\scriptsize
\setlength{\tabcolsep}{2pt}
\resizebox{\linewidth}{!}{%
\begin{tabular}{@{} l l r c c c c c r r @{}}
\toprule
Ticker & Regime & Days & B\&H & Agent & Gross & Fee & $\alpha$ & Ag. MDD & B\&H MDD \\
\midrule
RELIANCE & Bear & 111 & \mbox{-17.4\%} & \agentpct{-7.5} & \mbox{-6.5\%} & 1.0pp & \mbox{+9.9pp} & \mbox{5.1\%} & \mbox{21.0\%} \\
RELIANCE & Bull & 108 & \mbox{+15.1\%} & \agentpct{+5.6} & \mbox{+6.2\%} & 0.6pp & \mbox{-9.5pp} & \mbox{2.8\%} & \mbox{11.0\%} \\
TCS & Bear & 88 & \mbox{-20.4\%} & \agentpct{-4.8} & \mbox{-2.9\%} & 1.9pp & \mbox{+15.6pp} & \mbox{6.8\%} & \mbox{23.9\%} \\
TCS & Bull & 67 & \mbox{+21.9\%} & \agentpct{+19.6} & \mbox{+21.8\%} & 2.2pp & \mbox{-2.3pp} & \mbox{1.7\%} & \mbox{5.5\%} \\
\bottomrule
\end{tabular}%
}
\caption{Net return, gross return, fee drag, alpha vs B\&H, and MDD.}
\end{table}
\normalsize

**Table 4.** Excess Sharpe (6.5\% p.a.\ $R_f$), Sortino, Calmar (post-hoc on frozen equity).

\begin{table}[htbp]
\centering
\scriptsize
\begin{tabular}{@{} l l r r r r @{}}
\toprule
Ticker & Regime & Excess Sh. (agent) & Excess Sh. (B\&H) & Sortino & Calmar \\
\midrule
RELIANCE & Bear & -4.27 & -2.51 & -3.10 & -0.96 \\
RELIANCE & Bull & +0.74 & +1.25 & +3.67 & +1.94 \\
TCS & Bear & -2.69 & -3.13 & -2.25 & -0.71 \\
TCS & Bull & +3.86 & +3.27 & +24.22 & +11.88 \\
\bottomrule
\end{tabular}
\caption{Secondary risk-adjusted metrics; short windows make ratios noisy.}
\end{table}
\normalsize

**Patterns.** Bear (2/2): the agent generated smaller losses and lower MDD than B\&H; SELL-heavy signals in both windows. Bull: TCS nearly tracks B\&H; RELIANCE generated a positive return (+5.6\%) but lagged by about 9.5pp; fee drag (about 0.6pp) is insufficient to explain the gap; 74 SELL days in the bull window is the plausible binding factor. Internal bull stances can remain buy-leaning while final signals stay defensive.

**Capture and exposure.** Approximate upside/downside capture ratios reveal a ticker-level distinction. RELIANCE exhibits 43\% downside capture and 37\% upside capture, a near-symmetric reduction consistent with effective equity exposure below 1.0 rather than selective de-risking. TCS exhibits 24\% downside capture and 89\% upside capture, a meaningfully asymmetric profile. At N=1 these ratios are descriptive, not diagnostic, but they counsel caution in attributing RELIANCE bear outperformance to regime-aware coordination; a structurally low-exposure posture produces the same pattern mechanically.

**Ticker-vs-regime ambiguity.** The secondary risk-adjusted metrics (Table 4) reorganise the story: the agent exceeds B\&H excess Sharpe in both TCS windows and trails in both RELIANCE windows, a ticker-level split. This reading is equally consistent with the four data points as the regime framing. Neither interpretation is statistically supportable at N=4; both are noted for transparency.

**RELIANCE bear Sharpe note.** In the RELIANCE bear window the agent records a smaller absolute loss (\mbox{-7.5\%} vs \mbox{-17.4\%}) yet a worse excess Sharpe (\mbox{-4.27} vs \mbox{-2.51} for B\&H). A near-cash, low-volatility posture with a small negative excess return produces a large negative annualised Sharpe on a short window; this is a mechanical artefact of the ratio on concentrated SELL sequences, not a contradiction in the data.

### Figures

\begin{figure}[H]
\centering
\includegraphics[width=\linewidth]{figures/fig_regime_equity_grid.pdf}
\caption{Agent vs buy-and-hold equity (2$\times$2 grid).}
\end{figure}

\begin{figure}[H]
\centering
\includegraphics[width=\linewidth]{figures/fig_regime_returns_by_ticker.pdf}
\caption{Total returns (four windows).}
\end{figure}

\begin{figure}[H]
\centering
\includegraphics[width=\linewidth]{figures/fig_regime_signals_by_ticker.pdf}
\caption{Signal counts.}
\end{figure}

\begin{figure}[H]
\centering
\includegraphics[width=\linewidth]{figures/fig_regime_outlook_bullish.pdf}
\caption{Bullish analyst-outlook share.}
\end{figure}

\clearpage

## Conclusion

We presented a reproducible point-in-time LangGraph stack and a **scoped four-window case study**. Bear windows show lower loss and drawdown than B\&H; bull outcomes are heterogeneous. Risk-adjusted metrics split by ticker rather than regime---both framings are equally consistent with N=4 data points, and no causal claim about coordination quality is made.

**Limitations:** N=1 per window; two tickers; one LLM; anonymization not ablated; no multi-seed or index-universe evaluation; no latency CBS. **Future work:** seeds, broader PIT universes, anonymization ablations.

## Contributions

1. Reproducible backtest harness and frozen CSV artifacts.
2. Point-in-time policy and optional anonymization (ablation deferred to future work).
3. Structured Pydantic stage outputs.
4. Multi-agent graph with tool-bound analyst decomposition.
5. Honest regime-conditioned case study with documented limits.

## Acknowledgements {.unnumbered}

The agent graph implementation builds on **TradingAgents** (Xiao et al., 2024; Tauric Research, Apache License 2.0).

## References {.unnumbered}

B\u{a}dic\u{a}, C., B\u{a}dic\u{a}, A., Ganzha, M., Ivanovi\'c, M., Paprzycki, M., Seli\c{s}teanu, D. and Wrona, Z., 2025. Contemporary Agent Technology: LLM-Driven Advancements vs Classic Multi-Agent Systems. \textit{arXiv preprint} arXiv:2509.02515 [cs.MA]. \url{https://arxiv.org/abs/2509.02515}

Bailey, D.H., Borwein, J.M., L\'opez de Prado, M. and Zhu, Q.J., 2014. Pseudo-Mathematics and Financial Charlatanism: The Effects of Backtest Overfitting on Out-of-Sample Performance. \textit{Notices of the American Mathematical Society}, 61(5), pp.458--471. \url{https://doi.org/10.1090/noti1105}

Dewansh, S., 2026. Policy Convergence and Explainable Stability in Orchestrated Multi-Agent LLM Trading Frameworks. \textit{International Journal of Advanced Engineering and Management Science}, 12(2), pp.058--064. \url{https://doi.org/10.22161/ijaems.122.8}

Jeon, J. and Lee, H., 2026. Can Blindfolded LLMs Still Trade? An Anonymization-First Framework for Portfolio Optimization. \textit{arXiv preprint} arXiv:2603.17692 [cs.LG]. \url{https://arxiv.org/abs/2603.17692}

Li, X., Zeng, Y., Xing, X., Xu, J. and Xu, X., 2025. QuantAgents: Towards Multi-agent Financial System via Simulated Trading. In \textit{Findings of the Association for Computational Linguistics: EMNLP 2025}, pp.17438--17464, Suzhou, China. \url{https://doi.org/10.18653/v1/2025.findings-emnlp.945}

Miyazaki, K., Kawahara, T., Roberts, S. and Zohren, S., 2026. Toward Expert Investment Teams: A Multi-Agent LLM System with Fine-Grained Trading Tasks. \textit{arXiv preprint} arXiv:2602.23330 [cs.AI]. \url{https://arxiv.org/abs/2602.23330}

Nguyen, P. and Pham, T., 2026. Toward Reliable Evaluation of LLM-Based Financial Multi-Agent Systems: Taxonomy, Coordination Primacy, and Cost Awareness. \textit{arXiv preprint} arXiv:2603.27539 [cs.MA]. \url{https://arxiv.org/abs/2603.27539}

Papadakis, C., Filandrianos, G., Dimitriou, A., Lymperaiou, M., Thomas, K. and Stamou, G., 2025. StockSim: A Dual-Mode Order-Level Simulator for Evaluating Multi-Agent LLMs in Financial Markets. \textit{arXiv preprint} arXiv:2507.09255 [cs.CE]. \url{https://arxiv.org/abs/2507.09255}

Qian, L., Peng, X., Wang, Y., Zhang, V.J., He, H., Li, Z., Smith, H., Han, Y., He, Y., Li, H., Cao, Y., Yu, Y., Lopez-Lira, A., Lu, P., Nie, J.-Y., Xiong, G., Huang, J. and Ananiadou, S., 2026. When Agents Trade: Live Multi-Market Trading Arena for LLM Agents. In \textit{Proceedings of the ACM Web Conference 2026}. \url{https://doi.org/10.1145/3774904.3792821}

Xiao, Y., Sun, E., Luo, D. and Wang, W., 2024. TradingAgents: Multi-Agents LLM Financial Trading Framework. \textit{arXiv preprint} arXiv:2412.20138 [q-fin.TR]. \url{https://arxiv.org/abs/2412.20138}

Yang, H., Liu, X.-Y. and Wang, C.D., 2023. FinGPT: Open-Source Financial Large Language Models. \textit{arXiv preprint} arXiv:2306.06031 [q-fin.ST]. \url{https://arxiv.org/abs/2306.06031}

Yu, Y., Li, H., Chen, Z., Jiang, Y., Li, Y., Zhang, D., Liu, R., Suchow, J.W. and Khashanah, K., 2023. FinMem: A Performance-Enhanced LLM Trading Agent with Layered Memory and Character Design. \textit{arXiv preprint} arXiv:2311.13743 [q-fin.CP]. \url{https://arxiv.org/abs/2311.13743}

Zhao, T., Lyu, J., Jones, S., Garber, H., Pasquali, S. and Mehta, D., 2025. AlphaAgents: Large Language Model based Multi-Agents for Equity Portfolio Constructions. \textit{arXiv preprint} arXiv:2508.11152 [q-fin.ST]. \url{https://arxiv.org/abs/2508.11152}
