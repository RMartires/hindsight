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

/**
 * Vercel (and similar) rewrites buffer or drop long-lived SSE. In production the stream
 * URL must be an absolute https origin (via NEXT_PUBLIC_BACKEND_URL at build time).
 */
export function assertAbsoluteBackendStreamUrl(streamUrl: string): void {
  if (process.env.NODE_ENV !== "production") return;
  if (/^https?:\/\//i.test(streamUrl)) return;
  throw new Error(
    "Set NEXT_PUBLIC_BACKEND_URL to your public API base (e.g. https://api.example.com) in Vercel Environment Variables, then redeploy so the client bundle includes it. " +
      "SSE cannot use the /api rewrite. On the API, set CORS_ALLOWED_ORIGINS to include your Vercel site origin (e.g. https://your-app.vercel.app).",
  );
}
