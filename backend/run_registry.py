"""In-memory run state shared between analyze POST and SSE stream consumers."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional, TypedDict


class RunState(TypedDict):
    queue: asyncio.Queue
    snapshot: Dict[str, Any]


runs: Dict[str, RunState] = {}
run_timestamps: Dict[str, float] = {}


def complete_run(run_id: str) -> None:
    """Remove run metadata after the worker finishes or stream times out stale."""
    runs.pop(run_id, None)
    run_timestamps.pop(run_id, None)


def get_run(run_id: str) -> Optional[RunState]:
    return runs.get(run_id)
