import type { NextConfig } from "next";

/** Same origin as SSE (`NEXT_PUBLIC_BACKEND_URL`); defaults to local FastAPI in dev. */
function apiRewriteDestination(): string {
  const raw = process.env.NEXT_PUBLIC_BACKEND_URL?.trim();
  const base = (raw ? raw.replace(/\/$/, "") : "") || "http://localhost:8000";
  return `${base}/api/:path*`;
}

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: apiRewriteDestination(),
      },
    ];
  },
};

export default nextConfig;
