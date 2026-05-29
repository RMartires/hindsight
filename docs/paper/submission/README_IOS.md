# Algorithmic Finance (IOS Press) — submission package

Frozen E1: **four runs** (RELIANCE + TCS, bear + bull). See `docs/paper/claim-evidence-map.md`.

Regenerate figures before build:

```bash
MPLCONFIGDIR=.mpl_cache .venv/bin/python scripts/generate_paper_figures.py
./docs/paper/submission/build_ios_package.sh
```

Figures: `fig_regime_equity_grid`, `fig_regime_returns_by_ticker`, `fig_regime_signals_by_ticker`, `fig_regime_outlook_bullish`.
