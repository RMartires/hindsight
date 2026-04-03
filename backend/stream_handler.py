"""Bridge between TradingAgentsGraph.graph.stream() and SSE events."""

import asyncio
import json
import logging
import threading
from typing import Any, Dict, List, Optional

from config import build_config

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

        # Initialize state
        init_state = graph.propagator.create_initial_state(ticker, trade_date)
        args = graph.propagator.get_graph_args(callbacks=callbacks or None)

        # Track which reports/agents we've already emitted
        emitted_reports = set()
        agent_statuses: Dict[str, str] = {}

        def update_agent(name: str, status: str):
            if agent_statuses.get(name) != status:
                agent_statuses[name] = status
                _emit(queue, loop, "agent_status", {"agent": name, "status": status})

        # Set all agents to pending initially
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
            update_agent(agent, "pending")

        # Mark first analyst as in_progress
        first_agent = ANALYST_AGENT_NAMES[selected[0]]
        update_agent(first_agent, "in_progress")

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
                        _emit(queue, loop, "report", {
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
                    _emit(queue, loop, "debate", {
                        "phase": "investment",
                        "speaker": "Bull Researcher",
                        "content": bull_hist,
                    })
                if bear_hist and "bear_debate" not in emitted_reports:
                    emitted_reports.add("bear_debate")
                    _emit(queue, loop, "debate", {
                        "phase": "investment",
                        "speaker": "Bear Researcher",
                        "content": bear_hist,
                    })
                if judge and "invest_judge" not in emitted_reports:
                    emitted_reports.add("invest_judge")
                    update_agent("Bull Researcher", "completed")
                    update_agent("Bear Researcher", "completed")
                    update_agent("Research Manager", "completed")
                    _emit(queue, loop, "debate", {
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
                _emit(queue, loop, "report", {
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
                    _emit(queue, loop, "debate", {
                        "phase": "risk",
                        "speaker": "Aggressive Analyst",
                        "content": agg,
                    })
                if con and "risk_con" not in emitted_reports:
                    emitted_reports.add("risk_con")
                    update_agent("Conservative Analyst", "in_progress")
                    _emit(queue, loop, "debate", {
                        "phase": "risk",
                        "speaker": "Conservative Analyst",
                        "content": con,
                    })
                if neu and "risk_neu" not in emitted_reports:
                    emitted_reports.add("risk_neu")
                    update_agent("Neutral Analyst", "in_progress")
                    _emit(queue, loop, "debate", {
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
                    _emit(queue, loop, "debate", {
                        "phase": "risk",
                        "speaker": "Risk Judge",
                        "content": judge,
                    })

        # Final decision
        if trace:
            final_state = trace[-1]
            final_decision_text = final_state.get("final_trade_decision", "")
            decision = graph.process_signal(final_decision_text)

            # Mark all agents completed
            for agent in all_agents:
                update_agent(agent, "completed")

            _emit(queue, loop, "decision", {
                "final": decision,
                "full_text": final_decision_text,
                "investment_plan": final_state.get("investment_plan", ""),
            })

        _emit(queue, loop, "done", {"trace_id": trace_id or ""})

    except Exception as e:
        logger.exception("Analysis failed")
        _emit(queue, loop, "error", {"message": str(e)})
        _emit(queue, loop, "done", {"trace_id": trace_id or ""})
