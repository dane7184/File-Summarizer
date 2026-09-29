import { NextResponse } from "next/server";

export const runtime = "nodejs";

const PYTHON_API_URL = process.env.PYTHON_API_URL ?? "http://localhost:8000";

// Forwards the upload to the Python (FastAPI) service, which talks to Claude.
export async function POST(req: Request) {
  let form: FormData;
  try {
    form = await req.formData();
  } catch {
    return NextResponse.json({ error: "Invalid upload." }, { status: 400 });
  }

  let res: Response;
  try {
    res = await fetch(`${PYTHON_API_URL}/summarize`, { method: "POST", body: form });
  } catch {
    return NextResponse.json(
      { error: `Cannot reach the Python API at ${PYTHON_API_URL}. Is it running?` },
      { status: 502 }
    );
  }

  const body = await res.json().catch(() => null);
  if (!res.ok) {
    // FastAPI errors look like { detail: "..." }
    const message = typeof body?.detail === "string" ? body.detail : "Failed to summarize.";
    return NextResponse.json({ error: message }, { status: res.status });
  }

  return NextResponse.json({ summary: body?.summary ?? "", filename: body?.filename ?? "" });
}
