#!/usr/bin/env bash
# Build Algorithmic Finance / IOS Press submission PDF and DOCX from ios_manuscript.md.
# Requires: pandoc, and a PDF engine (tectonic recommended: brew install tectonic).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

STEM="Hindsight2020_AlgorithmicFinance_IOS_submission"

if ! command -v pandoc >/dev/null; then
  echo "Install pandoc: https://pandoc.org/" >&2
  exit 1
fi

PDF_ENGINE=""
if command -v tectonic >/dev/null; then
  PDF_ENGINE="tectonic"
elif command -v pdflatex >/dev/null; then
  PDF_ENGINE="pdflatex"
else
  echo "Need tectonic or pdflatex on PATH for PDF output." >&2
  exit 1
fi

pandoc ios_manuscript.md \
  -o "${STEM}.pdf" \
  --pdf-engine="$PDF_ENGINE" \
  --standalone \
  --number-sections

pandoc ios_manuscript.md \
  -o "${STEM}.docx" \
  --standalone \
  --number-sections

zip -r "${STEM}.zip" ios_manuscript.md README_IOS.md figures "${STEM}.pdf" "${STEM}.docx"

echo "Built: ${ROOT}/${STEM}.pdf, ${STEM}.docx, ${STEM}.zip"
