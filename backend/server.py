"""Hindsight 20/20 — FastAPI backend wrapping TradingAgentsGraph."""

import asyncio
import json
import os
import logging
import threading
import time
import uuid
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from stream_handler import run_analysis
from langfuse_api import fetch_trace, get_public_link
from supabase_runs import fetch_run_row, supabase_enabled

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _cors_allow_origins() -> List[str]:
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    extra = os.getenv("CORS_ALLOWED_ORIGINS", "").strip()
    if not extra:
        return origins
    for part in extra.split(","):
        o = part.strip()
        if o and o not in origins:
            origins.append(o)
    return origins


app = FastAPI(title="Hindsight 20/20", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_allow_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for active runs
runs: Dict[str, asyncio.Queue] = {}
# Track run creation time for cleanup
run_timestamps: Dict[str, float] = {}
# Max run age in seconds (1 hour)
MAX_RUN_AGE = 3600
# Max seconds between streamed events before treating the run as stalled (default 30 min)
STREAM_IDLE_TIMEOUT_SEC = float(os.getenv("STREAM_IDLE_TIMEOUT_SEC", "1800"))


class AnalyzeRequest(BaseModel):
    ticker: str
    trade_date: str
    analysts: Optional[List[str]] = None


class AnalyzeResponse(BaseModel):
    run_id: str
    trace_id: Optional[str] = None
    session_id: Optional[str] = None


@app.get("/api/health")
async def health():
    return {"status": "ok", "active_runs": len(runs)}


@app.get("/api/run-snapshot")
async def run_snapshot(
    trace_id: Optional[str] = Query(None),
    run_id: Optional[str] = Query(None),
):
    if not trace_id and not run_id:
        raise HTTPException(
            status_code=400, detail="Provide trace_id or run_id query parameter"
        )
    if not supabase_enabled():
        return {"hit": False}
    row = fetch_run_row(trace_id=trace_id, run_id=run_id)
    if not row:
        return {"hit": False}
    st = row.get("status")
    if st == "completed":
        return {
            "hit": True,
            "status": "completed",
            "payload": row.get("payload") or {},
            "ticker": row.get("ticker"),
            "trade_date": row.get("trade_date"),
        }
    if st == "failed":
        return {"hit": True, "status": "failed"}
    return {"hit": False}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    # Clean up stale runs
    _cleanup_stale_runs()

    run_id = str(uuid.uuid4())
    queue: asyncio.Queue = asyncio.Queue()
    runs[run_id] = queue
    run_timestamps[run_id] = time.time()

    # Generate Langfuse correlation IDs
    trace_id = None
    session_id = None
    try:
        from tradingagents.observability.langfuse_config import (
            langfuse_enabled,
            new_langfuse_run_correlation,
        )
        if langfuse_enabled():
            corr = new_langfuse_run_correlation(
                ticker=req.ticker, trade_date=req.trade_date
            )
            trace_id = corr.trace_id
            session_id = corr.session_id
    except Exception:
        logger.warning("Langfuse correlation generation failed", exc_info=True)

    loop = asyncio.get_event_loop()
    analysts = req.analysts or ["market", "fundamentals", "news", "social"]

    thread = threading.Thread(
        target=run_analysis,
        args=(run_id, req.ticker, req.trade_date, analysts, queue, loop, trace_id, session_id),
        daemon=True,
    )
    thread.start()

    return AnalyzeResponse(run_id=run_id, trace_id=trace_id, session_id=session_id)


@app.get("/api/stream/{run_id}")
async def stream(run_id: str):
    if run_id not in runs:
        raise HTTPException(status_code=404, detail="Run not found")

    queue = runs[run_id]

    async def event_generator():
        try:
            while True:
                event = await asyncio.wait_for(
                    queue.get(), timeout=STREAM_IDLE_TIMEOUT_SEC
                )
                event_type = event["type"]
                data = json.dumps(event["data"])
                yield {"event": event_type, "data": data}
                if event_type == "done":
                    break
        except asyncio.TimeoutError:
            yield {"event": "error", "data": json.dumps({"message": "Stream timeout"})}
            yield {"event": "done", "data": "{}"}
        finally:
            # Cleanup run after stream ends
            runs.pop(run_id, None)
            run_timestamps.pop(run_id, None)

    return EventSourceResponse(event_generator())


@app.get("/api/trace/{trace_id}")
async def get_trace(trace_id: str):
    result = fetch_trace(trace_id)
    if not result:
        raise HTTPException(status_code=404, detail="Trace not found")
    return result


@app.get("/api/trace/{trace_id}/link")
async def get_trace_link(trace_id: str):
    link = get_public_link(trace_id)
    if not link:
        raise HTTPException(status_code=404, detail="Could not generate link")
    return {"url": link}


def _cleanup_stale_runs():
    """Remove runs older than MAX_RUN_AGE."""
    now = time.time()
    stale = [rid for rid, ts in run_timestamps.items() if now - ts > MAX_RUN_AGE]
    for rid in stale:
        runs.pop(rid, None)
        run_timestamps.pop(rid, None)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
