from __future__ import annotations

from typing import Any, Mapping


def build_synthetic_investment_plan(state: Mapping[str, Any]) -> str:
    """
    Deterministic synthesis for ablations that skip the investment debate.

    This is intentionally not an LLM summarization. It preserves upstream evidence by
    carrying forward the analyst report text that exists for the current ablation.
    """
    sections: list[tuple[str, str]] = []

    market = str(state.get("market_report") or "").strip()
    if market:
        sections.append(("Market Analyst", market))

    sentiment = str(state.get("sentiment_report") or "").strip()
    if sentiment:
        sections.append(("Social Media Analyst", sentiment))

    news = str(state.get("news_report") or "").strip()
    if news:
        sections.append(("News Analyst", news))

    fundamentals = str(state.get("fundamentals_report") or "").strip()
    if fundamentals:
        sections.append(("Fundamentals Analyst", fundamentals))

    header = (
        "Synthesized investment plan from analyst report(s) below. "
        "Investment debate was disabled for this ablation."
    )

    if not sections:
        return header

    out = [header]
    for title, body in sections:
        out.append(f"\n\n## {title}\n{body}")
    return "".join(out).strip()


def synthetic_investment_plan_node(state: Mapping[str, Any]) -> dict[str, str]:
    """Graph node: set `investment_plan` from existing analyst reports."""
    return {"investment_plan": build_synthetic_investment_plan(state)}

