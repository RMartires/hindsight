# Hindsight 20/20

**Retro-temporal market analysis engine** — a dark, dashboard-first UI for running forensic-style multi-agent analysis on a **ticker** and **historical as-of date**. The backend wraps a LangGraph-powered **TradingAgents** pipeline, streams progress over **Server-Sent Events (SSE)**, and optionally correlates runs with **Langfuse** traces.

![Dashboard — pipeline, presets, and agent telemetry](docs/dashboard.png)

---

## What makes this repo interesting

### Point-in-time (“as of”) analysis

You choose a **trade date** and symbol; upstream agents pull data and narrative as if rewinding the clock. The UI ships **curated presets** (Pre-Lehman, Flash Crash, COVID bottom, FTX, GameStop, etc.) with sensible default tickers — useful for stress-testing the stack on well-known episodes.

### Agent pipeline, not a single chat box

Runs flow through specialist roles aligned with TradingAgents:

- **Market**, **Social**, **News**, and **Fundamentals** analysts produce structured reports.
- **Bull / Bear** researchers and the **Research Manager** run an **investment debate** phase.
- The **Trader** proposes a plan; **Aggressive / Conservative / Neutral** analysts and the **Risk Judge** run a **risk debate** phase.
- A **final trade decision** is emitted at the end of the graph stream.

The backend maps LangGraph stream chunks to stable agent names so the UI labels tools and statuses correctly (including tool sub-nodes).

### Live topology on the graph

On each run, the API emits a **`pipeline_topology`** event: nodes and edges extracted from the compiled LangGraph and **normalized** to the agents participating in that run — the React UI (@xyflow/react) renders the DAG you are actually executing.

### Transparent execution

SSE event types include:

| Event | Purpose |
|--------|---------|
| `pipeline_topology` | Graph structure for the run |
| `agent_status` | Pending / in progress / completed per agent |
| `graph_step` | Single-node graph updates when detectable |
| `tool_call` | Tool name, inputs/outputs (payload-capped), attributed to the active agent |
| `report` | Analyst reports and trader plan sections |
| `debate` | Investment- and risk-debate segments by speaker |
| `decision` | Parsed final decision + raw text |
| `done` / `error` | Run completion |

### Observability hooks

When Langfuse is configured, the backend generates **trace** and **session** IDs for correlation and exposes **`GET /api/trace/{trace_id}`** (structured span data for debugging) and **`GET /api/trace/{trace_id}/link`** (project URL when `LANGFUSE_PROJECT_ID` is set).

### Configuration mirrors TradingAgents

`backend/config.py` builds a config dict from environment variables loaded from **`.env` at the repository root** (LLM provider, OpenRouter vs OpenAI, model names, rate limits, debate rounds, optional **data vendor** overrides). Use `.env.example` in the repo root as a template.

### Frontend ↔ API ergonomics

- **`POST /api/analyze`** is proxied through Next.js rewrites for same-origin `fetch`.
- **SSE** connects **directly** to the FastAPI origin (`http://localhost:8000` in dev via `NEXT_PUBLIC_BACKEND_URL` or defaults) so the browser is not stuck behind a buffering proxy.

---

## Architecture

```mermaid
flowchart LR
  subgraph ui [Next.js 16 — localhost:3000]
    Page[Dashboard]
    SSE[EventSource SSE]
    API[fetch /api/analyze]
  end
  subgraph api [FastAPI — localhost:8000]
    Analyze[POST /api/analyze]
    Stream[GET /api/stream/:run_id]
    Health[GET /api/health]
    Trace[GET /api/trace/...]
  end
  subgraph engine [TradingAgents + LangGraph]
    Graph[TradingAgentsGraph.stream]
  end
  Page --> API
  API --> Analyze
  Analyze --> Graph
  Stream --> Graph
  Graph --> Stream
  SSE --> Stream
  Page --> SSE
```

---

## Repository layout

| Path | Role |
|------|------|
| `pyproject.toml` | Single dependency list: engine (`tradingagents`, `cli`), FastAPI stack, and tooling |
| `.env` / `.env.example` | Secrets and config at **repo root** (backend, scripts, and CLI) |
| `tradingagents/` | LangGraph multi-agent pipeline, dataflows, backtest helpers, LLM clients |
| `cli/` | Typer CLI (`tradingagents` console script) used by `main.py` and `scripts/backtest_mvp.py` |
| `scripts/` | `backtest_mvp.py`, `kite_token_server.py` |
| `main.py` | Standalone runner for the graph (loads `.env` from repo root) |
| `ROADMAP.md` | Engine / product roadmap notes |
| `backend/` | FastAPI app, SSE bridge, topology + tool extraction, Langfuse helpers |
| `frontend/` | Next.js App Router UI — pipeline canvas, controls, reports, debates |
| `frontend/lib/presets.ts` | Historical date / ticker presets |
| `docs/` | Project images (e.g. dashboard screenshot) |

---

## Prerequisites

- **Python 3.11+** (recommended) for the backend
- **Node.js** for the frontend (see `frontend/package.json` engines implied by Next 16)
- **API keys**: At minimum, keys for your chosen **LLM** provider and **market data** sources (see `.env.example` at the repo root).

---

## Quick start

### 1. Python (API + engine)

From the **repository root** (same directory as `pyproject.toml`):

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
cp .env.example .env
# Edit .env with your keys and provider settings.
python backend/server.py
# Serves on http://0.0.0.0:8000 — try GET /api/health
```

Use the same venv for `python scripts/backtest_mvp.py ...` or `tradingagents` from the root.

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env   # optional; see NEXT_PUBLIC_BACKEND_URL
npm run dev
```

Open **http://localhost:3000**, pick a preset or date + ticker, and start **New analysis**.

---

## API reference (summary)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Liveness + active run count |
| `POST` | `/api/analyze` | Body: `{ "ticker", "trade_date", "analysts"? }` → `{ run_id, trace_id?, session_id? }` |
| `GET` | `/api/stream/{run_id}` | SSE stream until `done` or timeout |
| `GET` | `/api/trace/{trace_id}` | Langfuse trace payload (if configured) |
| `GET` | `/api/trace/{trace_id}/link` | Trace URL in Langfuse UI |

---

## Tech stack

- **Frontend:** Next.js 16, React 19, TypeScript, **@xyflow/react**
- **Backend:** FastAPI, **sse-starlette**, **Langfuse** client (optional), **langgraph** (bundled with this repo)
- **Core graph:** `TradingAgentsGraph` + LangGraph streaming (`tradingagents/` package)

---

## License / attribution

The **TradingAgents**-style engine lives in this repository under `tradingagents/`; respect the license and terms of any data and model providers you configure.

If you extend the project, keep the repo-root `.env` out of version control (only `*.example` files are tracked).
