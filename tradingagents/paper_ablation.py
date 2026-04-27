"""Paper ablation presets for backtest (A1, A2, A3, full).

Maps ``PAPER_ABLATION`` to ``selected_analysts``, ``run_investment_debate``,
and ``run_risk_phase``. Unknown labels raise ``ValueError`` (backtest should exit non-zero).
"""

from __future__ import annotations

import os
from typing import Any, Dict, Final

PAPER_ABLATION_LABELS: Final[frozenset[str]] = frozenset({"a1", "a2", "a3", "full"})


def apply_paper_ablation_to_config(cfg: Dict[str, Any]) -> str:
    """Apply ablation to ``cfg`` in place. Returns the normalized label (``a1`` … ``full``)."""
    ablation = str(
        os.getenv("PAPER_ABLATION", cfg.get("paper_ablation", "full")) or "full"
    ).strip().lower()
    if ablation not in PAPER_ABLATION_LABELS:
        allowed = ", ".join(sorted(PAPER_ABLATION_LABELS))
        raise ValueError(
            f"Unknown PAPER_ABLATION {ablation!r}. Use one of: {allowed}."
        )
    cfg["paper_ablation"] = ablation
    if ablation == "a1":
        cfg["selected_analysts"] = ["market"]
        cfg["run_investment_debate"] = False
        cfg["run_risk_phase"] = False
    elif ablation == "a2":
        cfg["selected_analysts"] = ["market", "social", "news", "fundamentals"]
        cfg["run_investment_debate"] = False
        cfg["run_risk_phase"] = False
    elif ablation == "a3":
        cfg["selected_analysts"] = ["market", "social", "news", "fundamentals"]
        cfg["run_investment_debate"] = True
        cfg["run_risk_phase"] = False
    else:  # full
        cfg["selected_analysts"] = ["market", "social", "news", "fundamentals"]
        cfg["run_investment_debate"] = True
        cfg["run_risk_phase"] = True
    return ablation
