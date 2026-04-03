"""Extract LangChain/LangGraph tool results from stream chunks for SSE."""

from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple

MAX_PAYLOAD = 6000


def _json_safe(obj: Any, max_len: int = MAX_PAYLOAD) -> Optional[str]:
    """Serialize for SSE JSON; cap length."""
    if obj is None:
        return None
    if isinstance(obj, str):
        return obj if len(obj) <= max_len else obj[: max_len - 1] + "…"
    try:
        s = json.dumps(obj, default=str)
    except (TypeError, ValueError):
        s = str(obj)
    return s if len(s) <= max_len else s[: max_len - 1] + "…"


def _msg_type(m: Any) -> Optional[str]:
    t = getattr(m, "type", None)
    if t is None and isinstance(m, dict):
        t = m.get("type") or m.get("role")
    if t is None:
        return None
    return str(t).lower()


def _tool_meta(m: Any) -> Tuple[Optional[str], Any, Optional[str]]:
    if isinstance(m, dict):
        return (
            m.get("name"),
            m.get("content"),
            m.get("tool_call_id"),
        )
    return (
        getattr(m, "name", None),
        getattr(m, "content", None),
        getattr(m, "tool_call_id", None),
    )


def _is_tool_message(m: Any) -> bool:
    mt = _msg_type(m)
    if mt in ("tool", "toolmessage"):
        return True
    try:
        from langchain_core.messages import ToolMessage as LCToolMessage
        if isinstance(m, LCToolMessage):
            return True
    except Exception:
        pass
    return False


def _find_tool_input(msgs: List[Any], idx: int, tool_call_id: Optional[str]) -> Optional[str]:
    if not tool_call_id:
        return None
    for j in range(idx - 1, -1, -1):
        m = msgs[j]
        tcs = getattr(m, "tool_calls", None)
        if tcs is None and isinstance(m, dict):
            tcs = m.get("tool_calls")
        if not tcs:
            continue
        for tc in tcs:
            if isinstance(tc, dict):
                tid = tc.get("id")
                args = tc.get("args")
                if args is None and isinstance(tc.get("function"), dict):
                    args = tc["function"].get("arguments")
            else:
                tid = getattr(tc, "id", None)
                args = getattr(tc, "args", None)
            if tid == tool_call_id:
                if isinstance(args, str):
                    return _json_safe(args)
                return _json_safe(args)
    return None


def extract_tool_events_from_chunk(
    chunk: Dict[str, Any],
    caller_agent: Optional[str],
    emitted_signatures: Set[str],
    time_iso: str,
) -> List[Dict[str, Any]]:
    """
    Detect new tool result messages in chunk['messages'] and return event dicts
    for SSE type 'tool_call'.
    """
    if not caller_agent:
        return []
    msgs = chunk.get("messages")
    if msgs is None:
        return []
    if not isinstance(msgs, (list, tuple)):
        return []

    events: List[Dict[str, Any]] = []
    for i, m in enumerate(msgs):
        if not _is_tool_message(m):
            continue
        name, content, tid = _tool_meta(m)
        if not name:
            name = "tool"
        body = str(content) if content is not None else ""
        sig = f"{tid}:{name}:{hash(body)}"
        if sig in emitted_signatures:
            continue
        emitted_signatures.add(sig)

        inp = _find_tool_input(msgs, i, tid)
        ev_id = str(uuid.uuid4())
        events.append(
            {
                "id": ev_id,
                "agent": caller_agent,
                "tool_name": name,
                "input": inp,
                "output": _json_safe(content),
                "time": time_iso,
            }
        )
    return events
