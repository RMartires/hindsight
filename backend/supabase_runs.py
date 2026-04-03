"""Supabase persistence for completed / failed analysis runs (server-side only)."""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_client = None


def supabase_enabled() -> bool:
    return bool(os.getenv("SUPABASE_URL", "").strip() and os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip())


def _coerce_json(value: Any) -> Any:
    """Ensure payload is JSON-serializable for PostgREST."""
    try:
        json.dumps(value)
        return value
    except (TypeError, ValueError):
        return json.loads(json.dumps(value, default=str))


def get_supabase():
    global _client
    if not supabase_enabled():
        return None
    if _client is None:
        from supabase import create_client

        _client = create_client(
            os.environ["SUPABASE_URL"].strip(),
            os.environ["SUPABASE_SERVICE_ROLE_KEY"].strip(),
        )
    return _client


def upsert_terminal_run(
    *,
    run_id: str,
    trace_id: Optional[str],
    ticker: str,
    trade_date: str,
    status: str,
    payload: Dict[str, Any],
    error_message: Optional[str] = None,
) -> None:
    """Insert or replace row keyed by run_id."""
    client = get_supabase()
    if not client:
        return

    row = {
        "run_id": run_id,
        "trace_id": trace_id,
        "ticker": ticker,
        "trade_date": trade_date,
        "status": status,
        "payload": _coerce_json(payload),
        "error_message": error_message,
    }
    try:
        client.table("analysis_runs").upsert(row, on_conflict="run_id").execute()
    except Exception:
        logger.exception("Supabase upsert failed for run_id=%s", run_id)


def fetch_run_row(*, trace_id: Optional[str] = None, run_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    if not trace_id and not run_id:
        return None
    client = get_supabase()
    if not client:
        return None

    try:
        q = client.table("analysis_runs").select("*")
        if trace_id:
            q = q.eq("trace_id", trace_id)
        else:
            q = q.eq("run_id", run_id)
        res = q.limit(1).execute()
        rows = res.data or []
        return rows[0] if rows else None
    except Exception:
        logger.exception("Supabase fetch failed trace_id=%s run_id=%s", trace_id, run_id)
        return None
