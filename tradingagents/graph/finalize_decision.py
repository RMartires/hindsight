from __future__ import annotations

from typing import Any, Mapping


def finalize_decision_passthrough_node(state: Mapping[str, Any]) -> dict[str, str]:
    """
    Graph node for ablations that skip the risk phase.

    Copies the trader output into `final_trade_decision` so downstream code
    (backtests, state logging) can consistently read one field.
    """
    decision = str(state.get("trader_investment_plan") or "").strip()
    return {"final_trade_decision": decision}

