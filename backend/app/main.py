import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import summarize

load_dotenv()

app = FastAPI(title="File Summarizer API")

# Only needed if the browser calls this API directly. With the default setup,
# Next.js proxies the request, so CORS is not involved.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(summarize.router)


@app.get("/health")
def health():
    return {"status": "ok"}
