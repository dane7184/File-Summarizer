# File Summarizer (Next.js + Python)

Upload a PDF, .txt or .md file in the browser and get a summary from Claude.

```
Browser  ->  Next.js (port 3000)  ->  FastAPI (port 8000)  ->  Claude API
 upload UI     /api/summarize          POST /summarize
```

## Structure

```
file-summarizer/
├── frontend/                        Next.js app
│   ├── app/
│   │   ├── page.tsx                 page state and the call to /api/summarize
│   │   ├── components/
│   │   │   ├── FileUpload.tsx       drag and drop, validation, style picker
│   │   │   └── SummaryResult.tsx    summary display with copy button
│   │   └── api/summarize/route.ts   forwards the upload to the Python API
│   ├── package.json
│   └── ...
└── backend/                         FastAPI app
    ├── app/
    │   ├── main.py                  app setup, CORS, /health
    │   ├── routes/summarize.py      POST /summarize
    │   ├── services/
    │   │   ├── file_extractor.py    validates the upload; PDF or text
    │   │   └── summarizer.py        builds the prompt and calls Claude
    │   └── models/schemas.py        SummaryStyle, SummarizeResponse
    ├── requirements.txt
    └── .env.example
```

The API key lives only in the backend.

## 1. Run the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then put your ANTHROPIC_API_KEY in .env
uvicorn app.main:app --reload --port 8000
```

Check it: http://localhost:8000/health returns `{"status":"ok"}`. Interactive docs are at http://localhost:8000/docs.

## 2. Run the frontend

In a second terminal:

```bash
cd frontend
npm install
cp .env.example .env.local         # PYTHON_API_URL=http://localhost:8000
npm run dev
```

Open http://localhost:3000, choose a file and click Summarize.

## Limits

Files up to 20 MB. PDFs are sent to Claude as documents; text files are limited to 400,000 characters. Check the Claude API docs for the current PDF page and size limits: https://docs.claude.com

To support more file types (for example .docx), add a branch in `backend/app/services/file_extractor.py` that returns the extracted text.
