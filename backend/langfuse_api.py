"""Langfuse trace fetching and public link generation."""

import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def get_langfuse_rest_client():
    """Get a Langfuse client for REST API calls."""
    try:
        from langfuse import Langfuse

        base_url = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
        return Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            base_url=base_url,
        )
    except Exception:
        logger.exception("Failed to create Langfuse REST client")
        return None


def fetch_trace(trace_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a trace and transform it into a flowchart-friendly structure."""
    client = get_langfuse_rest_client()
    if not client:
        return None

    try:
        # Langfuse Python SDK v3+ exposes reads via the generated API client (not fetch_trace).
        trace_data = client.api.trace.get(trace_id)
        if not trace_data:
            return None

        # Build simplified node list from observations
        nodes = []
        observations = getattr(trace_data, "observations", []) or []
        for obs in observations:
            node = {
                "id": obs.id,
                "name": obs.name or "Unknown",
                "type": obs.type or "span",
                "status": "completed" if obs.end_time else "in_progress",
                "start_time": obs.start_time.isoformat() if obs.start_time else None,
                "end_time": obs.end_time.isoformat() if obs.end_time else None,
                "duration_ms": None,
            }
            if obs.start_time and obs.end_time:
                delta = obs.end_time - obs.start_time
                node["duration_ms"] = int(delta.total_seconds() * 1000)

            # Include a snippet of the output if available
            output = obs.output
            if isinstance(output, str) and len(output) > 500:
                output = output[:500] + "..."
            elif isinstance(output, dict):
                output = {k: str(v)[:200] for k, v in list(output.items())[:5]}
            node["output_preview"] = output

            nodes.append(node)

        # Sort by start time
        nodes.sort(key=lambda n: n["start_time"] or "")

        # Build edges (sequential based on time ordering)
        edges = []
        for i in range(len(nodes) - 1):
            edges.append({"from": nodes[i]["id"], "to": nodes[i + 1]["id"]})

        # Build Langfuse URL
        project_id = os.getenv("LANGFUSE_PROJECT_ID", "")
        base_url = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
        langfuse_url = f"{base_url}/project/{project_id}/traces/{trace_id}" if project_id else None

        return {
            "trace_id": trace_id,
            "nodes": nodes,
            "edges": edges,
            "langfuse_url": langfuse_url,
            "metadata": {
                "name": trace_data.name,
                "session_id": trace_data.session_id,
                "tags": trace_data.tags or [],
            },
        }

    except Exception:
        logger.exception("Failed to fetch trace %s", trace_id)
        return None


def get_public_link(trace_id: str) -> Optional[str]:
    """Generate or retrieve a public share link for a trace."""
    # Langfuse Python SDK doesn't have a direct "share" method.
    # Build the URL from known components.
    project_id = os.getenv("LANGFUSE_PROJECT_ID", "")
    base_url = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")

    if project_id:
        return f"{base_url}/project/{project_id}/traces/{trace_id}"
    return None
