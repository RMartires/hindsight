/**
 * Public backend origin for browser calls that must not use Next.js rewrites.
 * SSE through the dev proxy is buffered; connecting here keeps events low-latency.
 */
export function getBackendPublicOrigin(): string {
  const explicit = process.env.NEXT_PUBLIC_BACKEND_URL?.trim();
  if (explicit) {
    return explicit.replace(/\/$/, "");
  }
  if (process.env.NODE_ENV === "development") {
    return "http://localhost:8000";
  }
  return "";
}

export function backendStreamUrl(runId: string): string {
  const origin = getBackendPublicOrigin();
  const path = `/api/stream/${runId}`;
  return origin ? `${origin}${path}` : path;
}
