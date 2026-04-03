"""Bridge between TradingAgentsGraph.graph.stream() and SSE events."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set

from config import build_config
from pipeline_topology import (
    build_topology_payload,
    canonicalize_graph_node_id,
    maybe_graph_step_keys,
)
from tool_stream import extract_tool_events_from_chunk
from supabase_runs import upsert_terminal_run

logger = logging.getLogger(__name__)

# Analyst mappings (mirrors cli/main.py constants)
ANALYST_ORDER = ["market", "social", "news", "fundamentals"]
ANALYST_AGENT_NAMES = {
    "market": "Market Analyst",
    "social": "Social Analyst",
    "news": "News Analyst",
    "fundamentals": "Fundamentals Analyst",
}
ANALYST_REPORT_MAP = {
    "market": "market_report",
    "social": "sentiment_report",
    "news": "news_report",
    "fundamentals": "fundamentals_report",
}


def _emit(queue: asyncio.Queue, loop: asyncio.AbstractEventLoop, event_type: str, data: dict):
    """Thread-safe push of an SSE event onto the async queue."""
    loop.call_soon_threadsafe(queue.put_nowait, {"type": event_type, "data": data})


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _new_snapshot(run_id: str, trace_id: Optional[str], session_id: Optional[str]) -> dict:
    return {
        "status": "streaming",
        "agents": {},
        "reports": {},
        "debates": [],
        "decision": None,
        "traceId": trace_id,
        "runId": run_id,
        "sessionId": session_id,
        "activityLog": [],
        "error": None,
        "pipelineTopology": None,
        "lastGraphStep": None,
        "toolCalls": [],
    }


def _merge_snapshot(snap: dict, event_type: str, data: dict) -> None:
    if event_type == "agent_status":
        snap["agents"][data["agent"]] = data["status"]
    elif event_type == "pipeline_topology":
        snap["pipelineTopology"] = data
    elif event_type == "graph_step":
        snap["lastGraphStep"] = data
    elif event_type == "report":
        snap["reports"][data["section"]] = data["content"]
    elif event_type == "debate":
        snap["debates"].append(data)
    elif event_type == "decision":
        snap["decision"] = data
    elif event_type == "tool_call":
        snap["toolCalls"].append(data)
    elif event_type == "error":
        snap["error"] = data.get("message")


def run_analysis(
    run_id: str,
    ticker: str,
    trade_date: str,
    analysts: List[str],
    queue: asyncio.Queue,
    loop: asyncio.AbstractEventLoop,
    trace_id: Optional[str] = None,
    session_id: Optional[str] = None,
):
    """Run TradingAgentsGraph.graph.stream() in a background thread, emitting SSE events.

    This replicates the chunk-inspection logic from cli/main.py:1091-1192.
    """
    snapshot = _new_snapshot(run_id, trace_id, session_id)

    def emit(event_type: str, data: dict):
        _emit(queue, loop, event_type, data)
        _merge_snapshot(snapshot, event_type, data)

    try:
        config = build_config()
        selected = [a for a in ANALYST_ORDER if a in analysts]
        if not selected:
            selected = ["market", "fundamentals", "news", "social"]

        # Build callbacks (Langfuse handler if available)
        callbacks = []
        try:
            from tradingagents.observability.langfuse_config import get_langfuse_handler
            handler = get_langfuse_handler()
            if handler:
                callbacks.append(handler)
        except Exception:
            pass

        from tradingagents.graph.trading_graph import TradingAgentsGraph

        graph = TradingAgentsGraph(
            selected_analysts=selected,
            config=config,
            callbacks=callbacks,
        )

        try:
            topo = build_topology_payload(graph.graph, selected)
            emit("pipeline_topology", topo)
        except Exception:
            logger.warning("Failed to emit pipeline_topology", exc_info=True)

        # Initialize state
        init_state = graph.propagator.create_initial_state(ticker, trade_date)
        args = graph.propagator.get_graph_args(callbacks=callbacks or None)

        # Track which reports/agents we've already emitted
        emitted_reports = set()
        agent_statuses: Dict[str, str] = {}

        def update_agent(name: str, status: str):
            if agent_statuses.get(name) != status:
                agent_statuses[name] = status
                if status == "pending":
                    return
                emit(
                    "agent_status",
                    {"agent": name, "status": status, "time": _utc_iso()},
                )

        # Pending locally (no SSE) so the UI only shows in_progress / completed nodes.
        all_agents = []
        for key in selected:
            all_agents.append(ANALYST_AGENT_NAMES[key])
        all_agents.extend([
            "Bull Researcher", "Bear Researcher", "Research Manager",
            "Trader",
            "Aggressive Analyst", "Conservative Analyst", "Neutral Analyst",
            "Risk Judge",
        ])
        for agent in all_agents:
            agent_statuses[agent] = "pending"

        # Mark first analyst as in_progress
        first_agent = ANALYST_AGENT_NAMES[selected[0]]
        update_agent(first_agent, "in_progress")

        tool_emit_sigs: Set[str] = set()

        def active_caller_agent() -> Optional[str]:
            """First agent in pipeline order that is currently in_progress."""
            for aid in all_agents:
                if agent_statuses.get(aid) == "in_progress":
                    return aid
            return None

        trace = []
        for chunk in graph.graph.stream(init_state, **args):
            trace.append(chunk)

            # --- Analyst reports ---
            found_active = False
            for analyst_key in selected:
                agent_name = ANALYST_AGENT_NAMES[analyst_key]
                report_key = ANALYST_REPORT_MAP[analyst_key]
                has_report = bool(chunk.get(report_key))

                if has_report:
                    update_agent(agent_name, "completed")
                    if report_key not in emitted_reports:
                        emitted_reports.add(report_key)
                        emit("report", {
                            "section": report_key,
                            "content": chunk[report_key],
                        })
                elif not found_active:
                    update_agent(agent_name, "in_progress")
                    found_active = True

            # When all analysts done, start Bull Researcher
            if not found_active and selected:
                if agent_statuses.get("Bull Researcher") == "pending":
                    update_agent("Bull Researcher", "in_progress")

            # --- Investment debate ---
            debate = chunk.get("investment_debate_state")
            if debate:
                bull_hist = (debate.get("bull_history") or "").strip()
                bear_hist = (debate.get("bear_history") or "").strip()
                judge = (debate.get("judge_decision") or "").strip()

                if bull_hist or bear_hist:
                    update_agent("Bull Researcher", "in_progress")
                    update_agent("Bear Researcher", "in_progress")
                    update_agent("Research Manager", "in_progress")

                if bull_hist and "bull_debate" not in emitted_reports:
                    emitted_reports.add("bull_debate")
                    emit("debate", {
                        "phase": "investment",
                        "speaker": "Bull Researcher",
                        "content": bull_hist,
                    })
                if bear_hist and "bear_debate" not in emitted_reports:
                    emitted_reports.add("bear_debate")
                    emit("debate", {
                        "phase": "investment",
                        "speaker": "Bear Researcher",
                        "content": bear_hist,
                    })
                if judge and "invest_judge" not in emitted_reports:
                    emitted_reports.add("invest_judge")
                    update_agent("Bull Researcher", "completed")
                    update_agent("Bear Researcher", "completed")
                    update_agent("Research Manager", "completed")
                    emit("debate", {
                        "phase": "investment",
                        "speaker": "Research Manager",
                        "content": judge,
                    })
                    update_agent("Trader", "in_progress")

            # --- Trader ---
            trader_plan = chunk.get("trader_investment_plan")
            if trader_plan and "trader_plan" not in emitted_reports:
                emitted_reports.add("trader_plan")
                update_agent("Trader", "completed")
                emit("report", {
                    "section": "trader_investment_plan",
                    "content": trader_plan,
                })
                update_agent("Aggressive Analyst", "in_progress")

            # --- Risk debate ---
            risk = chunk.get("risk_debate_state")
            if risk:
                agg = (risk.get("aggressive_history") or "").strip()
                con = (risk.get("conservative_history") or "").strip()
                neu = (risk.get("neutral_history") or "").strip()
                judge = (risk.get("judge_decision") or "").strip()

                if agg and "risk_agg" not in emitted_reports:
                    emitted_reports.add("risk_agg")
                    update_agent("Aggressive Analyst", "in_progress")
                    emit("debate", {
                        "phase": "risk",
                        "speaker": "Aggressive Analyst",
                        "content": agg,
                    })
                if con and "risk_con" not in emitted_reports:
                    emitted_reports.add("risk_con")
                    update_agent("Conservative Analyst", "in_progress")
                    emit("debate", {
                        "phase": "risk",
                        "speaker": "Conservative Analyst",
                        "content": con,
                    })
                if neu and "risk_neu" not in emitted_reports:
                    emitted_reports.add("risk_neu")
                    update_agent("Neutral Analyst", "in_progress")
                    emit("debate", {
                        "phase": "risk",
                        "speaker": "Neutral Analyst",
                        "content": neu,
                    })
                if judge and "risk_judge" not in emitted_reports:
                    emitted_reports.add("risk_judge")
                    update_agent("Aggressive Analyst", "completed")
                    update_agent("Conservative Analyst", "completed")
                    update_agent("Neutral Analyst", "completed")
                    update_agent("Risk Judge", "completed")
                    emit("debate", {
                        "phase": "risk",
                        "speaker": "Risk Judge",
                        "content": judge,
                    })

            # Tool calls must run *after* status updates for this chunk, otherwise
            # active_caller_agent() still reflects the previous analyst and every tool
            # is mis-labeled (e.g. all as Market Analyst → wrong row in the UI).
            step_key = maybe_graph_step_keys(chunk)
            if step_key:
                emit(
                    "graph_step",
                    {"node_id": step_key, "time": _utc_iso()},
                )

            tool_caller: Optional[str] = None
            if step_key:
                tool_caller = canonicalize_graph_node_id(step_key)
            if not tool_caller:
                tool_caller = active_caller_agent()

            if isinstance(chunk, dict):
                ts = _utc_iso()
                for tool_ev in extract_tool_events_from_chunk(
                    chunk,
                    tool_caller,
                    tool_emit_sigs,
                    ts,
                ):
                    emit("tool_call", tool_ev)

        # Final decision
        if trace:
            final_state = trace[-1]
            final_decision_text = final_state.get("final_trade_decision", "")
            decision = graph.process_signal(final_decision_text)

            # Mark all agents completed
            for agent in all_agents:
                update_agent(agent, "completed")

            emit("decision", {
                "final": decision,
                "full_text": final_decision_text,
                "investment_plan": final_state.get("investment_plan", ""),
            })

        snapshot["status"] = "done"
        upsert_terminal_run(
            run_id=run_id,
            trace_id=trace_id,
            ticker=ticker,
            trade_date=trade_date,
            status="completed",
            payload=snapshot,
        )
        emit("done", {"trace_id": trace_id or ""})

    except Exception as e:
        logger.exception("Analysis failed")
        snapshot["status"] = "error"
        snapshot["error"] = str(e)
        upsert_terminal_run(
            run_id=run_id,
            trace_id=trace_id,
            ticker=ticker,
            trade_date=trade_date,
            status="failed",
            payload=snapshot,
            error_message=str(e),
        )
        emit("error", {"message": str(e)})
        emit("done", {"trace_id": trace_id or ""})
