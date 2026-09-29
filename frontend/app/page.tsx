"use client";

import { useState } from "react";
import FileUpload, { type SummaryStyle } from "./components/FileUpload";
import SummaryResult from "./components/SummaryResult";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState("");
  const [filename, setFilename] = useState("");
  const [error, setError] = useState("");

  function clear() {
    setSummary("");
    setFilename("");
    setError("");
  }

  async function handleSubmit(file: File, style: SummaryStyle) {
    clear();
    setLoading(true);
    try {
      const body = new FormData();
      body.append("file", file);
      body.append("style", style);
      const res = await fetch("/api/summarize", { method: "POST", body });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Something went wrong.");
      setSummary(data.summary);
      setFilename(data.filename ?? file.name);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <h1>File Summarizer</h1>
      <p className="subtitle">Upload a file and get a summary in seconds.</p>

      <FileUpload loading={loading} error={error} onSubmit={handleSubmit} onClear={clear} />

      {summary && <SummaryResult summary={summary} filename={filename} />}
    </main>
  );
}
