# Algorithmic Finance (IOS Press) — submission package

Generated for **[Algorithmic Finance](https://www.iospress.com/catalog/journals/algorithmic-finance)**.

| Deliverable | Purpose |
|-------------|---------|
| `ios_manuscript.md` | Master Markdown (double spacing via LaTeX at PDF build). |
| `Hindsight2020_AlgorithmicFinance_IOS_submission.pdf` | Primary upload candidate. |
| `Hindsight2020_AlgorithmicFinance_IOS_submission.docx` | Word alternative. |
| `figures/*.pdf` | Regime experiment figures (embedded in PDF). |

## Build

From repo root:

```bash
chmod +x docs/paper/submission/build_ios_package.sh
./docs/paper/submission/build_ios_package.sh
```

Regenerate figures first:

```bash
MPLCONFIGDIR=.mpl_cache .venv/bin/python scripts/generate_paper_figures.py
```

Requires **pandoc** and **tectonic** (or **pdflatex**).

## Frozen E1 artifacts

- `results/dates-REL-aug-2024-jan-2025-bear-dates.csv`
- `results/dates-REL-jan-2025-june-2025-bull-dates.csv`
- Analysis: `scripts/backtest_regime_analysis.ipynb`

See `docs/paper/claim-evidence-map.md`.

## Before you submit

1. Confirm author block on the title page of `ios_manuscript.md`.
2. Re-read live **[IOS instructions](https://www.iospress.com/catalog/journals/algorithmic-finance)**.
3. Decline optional gold open access for \$0 publication.
