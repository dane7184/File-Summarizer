"use client";

import { useRef, useState } from "react";

export type SummaryStyle = "bullets" | "short" | "detailed";

const MAX_MB = 20;
const ALLOWED_EXTENSIONS = [".pdf", ".txt", ".md"];

type Props = {
  loading: boolean;
  error: string;
  onSubmit: (file: File, style: SummaryStyle) => void;
  onClear: () => void;
};

export default function FileUpload({ loading, error, onSubmit, onClear }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [style, setStyle] = useState<SummaryStyle>("bullets");
  const [dragging, setDragging] = useState(false);
  const [localError, setLocalError] = useState("");

  function pick(f: File | undefined | null) {
    onClear();
    setLocalError("");
    if (!f) return;

    const name = f.name.toLowerCase();
    if (!ALLOWED_EXTENSIONS.some((ext) => name.endsWith(ext))) {
      setLocalError("Please choose a PDF, .txt or .md file.");
      return;
    }
    if (f.size > MAX_MB * 1024 * 1024) {
      setLocalError(`File is too large. Maximum size is ${MAX_MB} MB.`);
      return;
    }
    setFile(f);
  }

  function remove() {
    setFile(null);
    setLocalError("");
    onClear();
    if (inputRef.current) inputRef.current.value = "";
  }

  const shownError = localError || error;

  return (
    <div className="card">
      <div
        className={`dropzone${dragging ? " active" : ""}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          pick(e.dataTransfer.files?.[0]);
        }}
      >
        <strong>Drag and drop a file here, or click to browse</strong>
        <span className="hint">PDF, TXT or Markdown, up to {MAX_MB} MB</span>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.txt,.md,application/pdf,text/plain,text/markdown"
          hidden
          onChange={(e) => pick(e.target.files?.[0])}
        />
      </div>

      {file && (
        <div className="file-row">
          <span className="file-name">
            {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
          </span>
          <button className="link-btn" onClick={remove} disabled={loading}>
            Remove
          </button>
        </div>
      )}

      <div className="controls">
        <select
          value={style}
          onChange={(e) => setStyle(e.target.value as SummaryStyle)}
          disabled={loading}
          aria-label="Summary style"
        >
          <option value="bullets">Bullet points</option>
          <option value="short">Short paragraph</option>
          <option value="detailed">Detailed</option>
        </select>
        <button
          className="primary"
          onClick={() => file && onSubmit(file, style)}
          disabled={!file || loading}
        >
          {loading && <span className="spinner" />}
          {loading ? "Summarizing..." : "Summarize"}
        </button>
      </div>

      {shownError && <div className="error">{shownError}</div>}
    </div>
  );
}
