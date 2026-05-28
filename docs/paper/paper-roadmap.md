# Hindsight 20/20 — Paper roadmap & progress

> Scope bounded by **`.cursor/memory.md`**. Engineering backlog: repo-root **`ROADMAP.md`** (not paper tasks).

**Submission draft:** [manuscript.md](manuscript.md)

**Last updated:** 2026-05-28.

**Done since regime pivot:** **Frozen E1** regime CSVs + definition in [claim-evidence-map.md](claim-evidence-map.md); **`scripts/backtest_regime_analysis.ipynb`**; **`scripts/generate_paper_figures.py`** → **`fig_regime_*`**; ablation artifacts moved to **`results/_retired/`**; manuscript rewrite in progress.

**Blocking submission:** author placeholders in **`ios_manuscript.md`**; portal declarations; rebuild IOS PDF after manuscript sync.

---

## Venue

**[Algorithmic Finance](https://www.iospress.com/catalog/journals/algorithmic-finance)** (IOS Press, \$0 default track; decline optional gold OA).

| Topic | Note |
|-------|------|
| Abstract | ≤200 words — trim in `ios_manuscript.md` |
| References | Harvard at export |
| Submission | `docs/paper/submission/` — `build_ios_package.sh` |

---

## `docs/paper/` layout

| File | Role |
|------|------|
| [manuscript.md](manuscript.md) | Paper draft |
| [claim-evidence-map.md](claim-evidence-map.md) | **Frozen E1** regime table + regime definition |
| [STORY_LOCK.md](STORY_LOCK.md) | Title, S1–S5 |
| [outline.md](outline.md) | Section skeleton |
| [paper-roadmap.md](paper-roadmap.md) | This file |
| [bib-seed.bib](bib-seed.bib) | Starter refs |
| [submission/](submission/) | IOS package |

---

## Progress toward submission PDF

| Track | Status |
|-------|--------|
| Prose (`manuscript.md`) | 🟡 Regime §4 drafted; sync `ios_manuscript.md` |
| Empirical freeze | ✅ Frozen E1 bear + bull CSVs |
| Figures | ✅ `fig_regime_equity`, `fig_regime_returns`, `fig_regime_signals`, `fig_regime_outlook_bullish` |
| LLM | ✅ `qwen/qwen3.5-flash-02-23` |
| Pipeline | ✅ `PAPER_ABLATION=full` |
| Bibliography | 🔁 Seed only |
| IOS PDF | 🟡 Rebuild after sync |

**Legend:** ✅ done · 🟡 draft · ⬜ not started · 🔁 optional

### Experiments (Frozen E1)

| Item | Artifact |
|------|----------|
| Bear run | `results/dates-REL-aug-2024-jan-2025-bear-dates.csv` |
| Bull run (through 2025-05-16) | `results/dates-REL-jan-2025-june-2025-bull-dates.csv` |
| Analysis | `scripts/backtest_regime_analysis.ipynb` |
| Figures CLI | `scripts/generate_paper_figures.py` |
| Retired | `results/_retired/` (ablation CSVs, old `dates.csv`) |

---

## Rule of thumb

Claims must match **`.cursor/memory.md`** and **Frozen E1** artifacts. Regime labels are **exogenous** (underlying return), not agent outlooks.
