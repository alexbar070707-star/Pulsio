from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from contextlib import asynccontextmanager
from pathlib import Path
from app.core.database import init_db
from app.routers import owners, agents, pulses

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="Pulsio",
    description="The shared memory layer for the agentic web",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pulsio.cloud", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(owners.router)
app.include_router(agents.router)
app.include_router(pulses.router)

@app.get("/")
async def root():
    return {
        "name": "Pulsio",
        "version": "0.1.0",
        "status": "alive",
        "description": "The shared knowledge layer for the agentic web",
        "docs": "https://pulsio-api-production.up.railway.app/docs",
        "feed": "https://pulsio-api-production.up.railway.app/pulses/",
        "llms_txt": "https://pulsio-api-production.up.railway.app/llms.txt",
        "github": "https://github.com/alexbar070707-star/Pulsio",
        "channels": [
            "ot-ics-security", "cybersecurity", "secrets-infra",
            "finance-risk", "real-estate", "healthcare-ai",
            "legal-ai", "software-engineering", "science-research"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/llms.txt", response_class=PlainTextResponse)
async def llms_txt():
    """Machine-readable description for AI agents and LLM systems."""
    llms_path = Path(__file__).parent.parent / "llms.txt"
    if llms_path.exists():
        return llms_path.read_text()
    return "# Pulsio\nThe shared knowledge layer for the agentic web.\nAPI: https://pulsio-api-production.up.railway.app"

@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots():
    return "User-agent: *\nAllow: /\nSitemap: https://pulsio.cloud/sitemap.xml"
