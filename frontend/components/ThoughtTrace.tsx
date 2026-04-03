"use client";

import { useEffect, useState } from "react";

interface TraceNode {
  id: string;
  name: string;
  type: string;
  status: string;
  duration_ms: number | null;
  output_preview: unknown;
}

interface TraceData {
  trace_id: string;
  nodes: TraceNode[];
  langfuse_url: string | null;
  metadata: {
    name: string;
    session_id: string;
    tags: string[];
  };
}

interface Props {
  traceId: string | null;
}

export default function ThoughtTrace({ traceId }: Props) {
  const [trace, setTrace] = useState<TraceData | null>(null);
  const [loading, setLoading] = useState(false);
  const [linkUrl, setLinkUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!traceId) return;

    let cancelled = false;

    async function load() {
      setLoading(true);
      try {
        const [traceRes, linkRes] = await Promise.all([
          fetch(`/api/trace/${traceId}`),
          fetch(`/api/trace/${traceId}/link`),
        ]);

        if (cancelled) return;

        const traceData = traceRes.ok ? await traceRes.json() : null;
        setTrace(traceData);

        const linkData = linkRes.ok ? await linkRes.json() : null;
        if (linkData?.url) setLinkUrl(linkData.url);
      } catch {
        // ignore
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, [traceId]);

  if (!traceId) return null;

  return (
    <div className="thought-trace">
      <h3 className="section-title">Agent Thought Trace</h3>

      {loading && <p className="trace-loading">Loading trace data...</p>}

      {trace && (
        <div className="trace-timeline">
          {trace.nodes.map((node) => (
            <div key={node.id} className="trace-node">
              <div className="trace-node-header">
                <span className="trace-node-name">{node.name}</span>
                {node.duration_ms && (
                  <span className="trace-node-duration">
                    {(node.duration_ms / 1000).toFixed(1)}s
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {linkUrl && (
        <a
          href={linkUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="trace-link"
        >
          View full trace in Langfuse &rarr;
        </a>
      )}
    </div>
  );
}
