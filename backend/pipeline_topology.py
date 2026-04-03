"""Extract and normalize LangGraph topology for the pipeline SSE + frontend."""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# Keys that appear in full-state stream chunks (not LangGraph node ids in "updates" mode).
STREAM_STATE_KEYS = frozenset(
    {
        "market_report",
        "sentiment_report",
        "news_report",
        "fundamentals_report",
        "investment_debate_state",
        "risk_debate_state",
        "trader_investment_plan",
        "final_trade_decision",
        "investment_plan",
        "messages",
    }
)

_PROG = re.compile(r"\s*\(\d+/\d+\)\s*$")


def _strip_progress_suffix(raw: str) -> str:
    return _PROG.sub("", raw).strip()


def canonicalize_graph_node_id(raw_id: str) -> Optional[str]:
    """Map a LangGraph node id / label to the display agent id used by the UI."""
    if not raw_id or raw_id.startswith("__"):
        return None
    s = _strip_progress_suffix(raw_id.strip())
    low = s.lower().replace("_", " ").replace("-", " ")

    if low in ("market analyst",) or ("market" in low and "analyst" in low and "fundamental" not in low):
        return "Market Analyst"
    if ("social" in low and "analyst" in low) or low == "social analyst":
        return "Social Analyst"
    if ("news" in low and "analyst" in low) or low == "news analyst":
        return "News Analyst"
    if "fundamental" in low and "analyst" in low:
        return "Fundamentals Analyst"
    if "bull" in low and "research" in low:
        return "Bull Researcher"
    if "bear" in low and "research" in low:
        return "Bear Researcher"
    if "research manager" in low:
        return "Research Manager"
    if low == "trader":
        return "Trader"
    if "trader" in low and "tool" not in low and "analyst" not in low:
        return "Trader"
    if "aggressive" in low and "analyst" in low:
        return "Aggressive Analyst"
    if "conservative" in low and "analyst" in low:
        return "Conservative Analyst"
    if "neutral" in low and "analyst" in low:
        return "Neutral Analyst"
    if "risk" in low and "judge" in low:
        return "Risk Judge"

    return None


def agents_in_run(selected_analyst_keys: List[str]) -> Set[str]:
    """Display agent ids that participate in this run (analysts + fixed tail)."""
    order = ["market", "social", "news", "fundamentals"]
    key_to_name = {
        "market": "Market Analyst",
        "social": "Social Analyst",
        "news": "News Analyst",
        "fundamentals": "Fundamentals Analyst",
    }
    selected = [key_to_name[k] for k in order if k in selected_analyst_keys]
    tail = [
        "Bull Researcher",
        "Bear Researcher",
        "Research Manager",
        "Trader",
        "Aggressive Analyst",
        "Conservative Analyst",
        "Neutral Analyst",
        "Risk Judge",
    ]
    return set(selected) | set(tail)


def extract_raw_topology(compiled: Any) -> Dict[str, Any]:
    """Return {\"nodes\": [{id, label}], \"edges\": [{from, to}], \"source\": str}."""
    empty = {"nodes": [], "edges": [], "source": "empty"}
    try:
        getter = getattr(compiled, "get_graph", None)
        if not callable(getter):
            return {**empty, "source": "no_get_graph"}
        g = getter()
        if g is None:
            return {**empty, "source": "null_graph"}
    except Exception as e:
        logger.warning("get_graph failed: %s", e)
        return {**empty, "source": f"error:{type(e).__name__}"}

    nodes_out: List[Dict[str, str]] = []
    edges_out: List[Dict[str, str]] = []

    raw_nodes = getattr(g, "nodes", None)
    if isinstance(raw_nodes, dict):
        for nid in raw_nodes:
            sid = str(nid)
            nodes_out.append({"id": sid, "label": sid})
    elif raw_nodes is not None:
        try:
            for nid in raw_nodes:
                sid = str(nid)
                nodes_out.append({"id": sid, "label": sid})
        except TypeError:
            pass

    raw_edges = getattr(g, "edges", None) or []
    for e in raw_edges:
        src: Optional[str] = None
        tgt: Optional[str] = None
        if hasattr(e, "source") and hasattr(e, "target"):
            src, tgt = str(e.source), str(e.target)
        elif isinstance(e, (list, tuple)) and len(e) >= 2:
            src, tgt = str(e[0]), str(e[1])
        elif isinstance(e, dict):
            src = str(e.get("source") or e.get("from") or "")
            tgt = str(e.get("target") or e.get("to") or "")
        if src and tgt:
            edges_out.append({"from": src, "to": tgt})

    return {
        "nodes": nodes_out,
        "edges": edges_out,
        "source": "langgraph",
    }


def normalize_topology_for_run(
    raw: Dict[str, Any],
    selected_analyst_keys: List[str],
) -> Dict[str, Any]:
    """Collapse LangGraph ids to UI agent ids; keep only edges inside this run's agent set."""
    allowed = agents_in_run(selected_analyst_keys)
    seen_edges: Set[tuple[str, str]] = set()
    norm_edges: List[Dict[str, str]] = []
    norm_nodes: Dict[str, str] = {}

    for e in raw.get("edges") or []:
        a = canonicalize_graph_node_id(e.get("from") or "")
        b = canonicalize_graph_node_id(e.get("to") or "")
        if not a or not b or a not in allowed or b not in allowed:
            continue
        key = (a, b)
        if key in seen_edges:
            continue
        seen_edges.add(key)
        norm_edges.append({"from": a, "to": b})
        norm_nodes[a] = a
        norm_nodes[b] = b

    nodes_list = [{"id": nid, "label": nid} for nid in sorted(norm_nodes)]

    return {
        "nodes": nodes_list,
        "edges": norm_edges,
        "raw_node_count": len(raw.get("nodes") or []),
        "raw_edge_count": len(raw.get("edges") or []),
        "source": raw.get("source") or "normalized",
    }


def build_topology_payload(compiled: Any, selected_analyst_keys: List[str]) -> Dict[str, Any]:
    raw = extract_raw_topology(compiled)
    normalized = normalize_topology_for_run(raw, selected_analyst_keys)
    return {
        "nodes": normalized["nodes"],
        "edges": normalized["edges"],
        "raw_node_count": normalized["raw_node_count"],
        "raw_edge_count": normalized["raw_edge_count"],
        "source": normalized["source"],
    }


def maybe_graph_step_keys(chunk: Any) -> Optional[str]:
    """If the stream chunk looks like a single-node update, return that node key."""
    if not isinstance(chunk, dict):
        return None
    extras = [
        k
        for k in chunk
        if k not in STREAM_STATE_KEYS and not str(k).startswith("__")
    ]
    if len(extras) == 1:
        return str(extras[0])
    return None
