"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Props {
  /** Raw markdown (may grow incrementally while streaming). */
  source: string;
  className?: string;
}

export default function MarkdownContent({ source, className = "" }: Props) {
  const text = source?.trim() ? source : "—";
  return (
    <div className={`markdown-body ${className}`.trim()}>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
    </div>
  );
}
