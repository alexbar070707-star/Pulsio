from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
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
    return {"name": "Pulsio", "version": "0.1.0", "status": "alive"}

@app.get("/health")
async def health():
    return {"status": "ok"}
