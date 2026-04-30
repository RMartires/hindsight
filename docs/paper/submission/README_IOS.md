# Algorithmic Finance (IOS Press) — submission package

Generated sources for **[Algorithmic Finance](https://www.iospress.com/catalog/journals/algorithmic-finance)** author instructions:

| Deliverable | Purpose |
|-------------|---------|
| `ios_manuscript.md` | Master Markdown (double spacing and numbering applied at PDF build via LaTeX). |
| `Hindsight2020_AlgorithmicFinance_IOS_submission.pdf` | Primary upload candidate (figures embedded). |
| `Hindsight2020_AlgorithmicFinance_IOS_submission.docx` | Word alternative; **set double spacing** in Word if IOS requires it (pandoc does not enforce this in DOCX). |
| `Hindsight2020_AlgorithmicFinance_IOS_submission.zip` | Convenience bundle for upload / archiving. |
| `figures/*.pdf` | Copy of publication figures (also embedded in PDF). |

## Build

From repo root:

```bash
chmod +x docs/paper/submission/build_ios_package.sh
./docs/paper/submission/build_ios_package.sh
```

Requires **pandoc** and **tectonic** (or **pdflatex**).

## Before you submit

1. Replace bracketed placeholders on the title page of `ios_manuscript.md`: **[Corresponding Author Name]**, **[City, Country]**, **[email@example.com]**.
2. Re-read live **[IOS instructions](https://www.iospress.com/catalog/journals/algorithmic-finance)** — layout rules can change; confirm single-file vs separate figure sheets.
3. Fill journal portal declarations; **decline optional gold open access** if you want \$0 publication.
