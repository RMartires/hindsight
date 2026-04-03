-- Run in Supabase SQL Editor or via supabase db push.
-- Caches terminal analysis runs for UI replay (completed / failed).

create table if not exists public.analysis_runs (
    run_id text primary key,
    trace_id text unique,
    status text not null check (status in ('completed', 'failed')),
    payload jsonb not null default '{}'::jsonb,
    error_message text,
    ticker text,
    trade_date text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint analysis_runs_trace_or_run check (trace_id is not null or run_id is not null)
);

create index if not exists analysis_runs_trace_id_idx on public.analysis_runs (trace_id)
    where trace_id is not null;

-- Backend uses service role only; optional: enable RLS and omit policies for anon/authenticated.
-- alter table public.analysis_runs enable row level security;
