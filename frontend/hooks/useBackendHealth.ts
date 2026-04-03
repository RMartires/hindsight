"use client";

import { useEffect, useState } from "react";

interface BackendHealthResponse {
  status: string;
  active_runs: number;
}

export interface BackendHealthState {
  status: string | null;
  activeRuns: number;
  error: string | null;
}

export function useBackendHealth(pollMs: number = 15000): BackendHealthState {
  const [state, setState] = useState<BackendHealthState>({
    status: null,
    activeRuns: 0,
    error: null,
  });

  useEffect(() => {
    let mounted = true;

    async function fetchHealth() {
      try {
        const res = await fetch("/api/health");
        const data: BackendHealthResponse = await res.json();
        if (!mounted) return;
        if (!res.ok) {
          setState({ status: null, activeRuns: 0, error: `HTTP ${res.status}` });
          return;
        }
        setState({ status: data.status, activeRuns: data.active_runs, error: null });
      } catch (err) {
        if (!mounted) return;
        setState((s) => ({
          ...s,
          error: err instanceof Error ? err.message : "Health check failed",
        }));
      }
    }

    fetchHealth();
    const interval = setInterval(fetchHealth, pollMs);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [pollMs]);

  return state;
}

