"use client";

import { useState } from "react";

type Props = {
  summary: string;
  filename: string;
};

export default function SummaryResult({ summary, filename }: Props) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(summary);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // Clipboard can be unavailable (for example on plain http); ignore.
    }
  }

  return (
    <div className="card result">
      <div className="result-header">
        <h2>Summary</h2>
        <button className="link-btn" onClick={copy}>
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
      <p className="result-file">{filename}</p>
      <div className="summary">{summary}</div>
    </div>
  );
}
