"""Extract LLM token usage from LangGraph stream chunks (LangChain messages)."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Set, Tuple


def get_llm_pricing_usd_per_million() -> Tuple[float, float]:
    """USD per 1M tokens. Zero means omit cost estimate."""
    try:
        inp = float(os.getenv("LLM_PRICE_INPUT_PER_1M_TOKENS", "0") or 0)
        out = float(os.getenv("LLM_PRICE_OUTPUT_PER_1M_TOKENS", "0") or 0)
    except ValueError:
        return 0.0, 0.0
    return max(0.0, inp), max(0.0, out)


def estimate_usd_for_tokens(input_tokens: int, output_tokens: int) -> Optional[float]:
    pin, pout = get_llm_pricing_usd_per_million()
    if pin <= 0 and pout <= 0:
        return None
    return (input_tokens * pin + output_tokens * pout) / 1_000_000.0


def _msg_type(m: Any) -> Optional[str]:
    t = getattr(m, "type", None)
    if t is None and isinstance(m, dict):
        t = m.get("type") or m.get("role")
    if t is None:
        return None
    return str(t).lower()


def _is_ai_message(m: Any) -> bool:
    mt = _msg_type(m)
    if mt in ("ai", "aimessage", "assistant"):
        return True
    try:
        from langchain_core.messages import AIMessage

        if isinstance(m, AIMessage):
            return True
    except Exception:
        pass
    return False


def _usage_dict_from_message(m: Any) -> Tuple[Optional[dict], Optional[dict]]:
    um = getattr(m, "usage_metadata", None)
    if um is None and isinstance(m, dict):
        um = m.get("usage_metadata")
    rm = getattr(m, "response_metadata", None)
    if rm is None and isinstance(m, dict):
        rm = m.get("response_metadata")
    um_dict = um if isinstance(um, dict) else None
    rm_dict = rm if isinstance(rm, dict) else None
    return um_dict, rm_dict


def _coerce_int(v: Any) -> Optional[int]:
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _tokens_from_usage(um: Optional[dict], rm: Optional[dict]) -> Optional[Tuple[int, int]]:
    inp: Optional[int] = None
    out: Optional[int] = None
    if um:
        inp = _coerce_int(
            um.get("input_tokens")
            if um.get("input_tokens") is not None
            else um.get("prompt_tokens")
        )
        out = _coerce_int(
            um.get("output_tokens")
            if um.get("output_tokens") is not None
            else um.get("completion_tokens")
        )
    if (inp is None or out is None) and rm:
        tu = rm.get("token_usage")
        if isinstance(tu, dict):
            if inp is None:
                inp = _coerce_int(
                    tu.get("prompt_tokens") if tu.get("prompt_tokens") is not None else tu.get("input_tokens")
                )
            if out is None:
                out = _coerce_int(
                    tu.get("completion_tokens")
                    if tu.get("completion_tokens") is not None
                    else tu.get("output_tokens")
                )
    if inp is None or out is None:
        total = None
        if um:
            total = _coerce_int(um.get("total_tokens"))
        if total is None and rm and isinstance(rm.get("token_usage"), dict):
            total = _coerce_int(rm["token_usage"].get("total_tokens"))
        if total is not None and inp is not None and out is None:
            out = max(0, total - inp)
        elif total is not None and out is not None and inp is None:
            inp = max(0, total - out)
        elif total is not None and inp is None and out is None:
            return None

    if inp is None or out is None:
        return None
    if inp < 0 or out < 0:
        return None
    return inp, out


def _dedupe_key_for_message(m: Any, inp: int, out: int) -> str:
    mid = getattr(m, "id", None)
    if mid is None and isinstance(m, dict):
        mid = m.get("id")
    if mid:
        return str(mid)
    content = getattr(m, "content", None)
    if content is None and isinstance(m, dict):
        content = m.get("content")
    if isinstance(content, list):
        content = str(content)
    elif content is None:
        content = ""
    else:
        content = str(content)
    return f"nocid:{inp}:{out}:{len(content)}:{hash(content[:4000])}"


def extract_llm_usage_events_from_chunk(
    chunk: Dict[str, Any],
    agent: str,
    node_id: str,
    time_iso: str,
    seen_message_keys: Set[str],
) -> List[Dict[str, Any]]:
    """
    Find new AIMessages with usage and return llm_usage event payloads (without run totals).
    Caller attributes agent/node from the same graph step as tool_call events.
    """
    msgs = chunk.get("messages")
    if msgs is None or not isinstance(msgs, (list, tuple)):
        return []

    events: List[Dict[str, Any]] = []
    for m in msgs:
        if not _is_ai_message(m):
            continue
        um, rm = _usage_dict_from_message(m)
        parsed = _tokens_from_usage(um, rm)
        if not parsed:
            continue
        inp, out = parsed
        key = _dedupe_key_for_message(m, inp, out)
        if key in seen_message_keys:
            continue
        seen_message_keys.add(key)

        delta_usd = estimate_usd_for_tokens(inp, out)
        events.append(
            {
                "agent": agent,
                "node_id": node_id,
                "input_tokens": inp,
                "output_tokens": out,
                "time": time_iso,
                "estimated_usd_delta": delta_usd,
            }
        )
    return events
