"""FastAPI application entrypoint.

Run locally with:

    uvicorn app.main:app --reload

Interactive docs (Swagger UI):  http://127.0.0.1:8000/docs
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401  (register ORM models with the metadata)
from app.db import Base, engine
from app.routers import history, queues


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Queueing Theory API",
    version="0.1.0",
    description=(
        "REST API for queueing-theory calculations. "
        "Computes steady-state metrics of **M/M/1** and **M/D/1** queues "
        "(closed-form and Monte-Carlo simulation) and keeps a history of "
        "calculations. Formulas follow Bocharov & Pechinkin, "
        "*Queueing Theory*, pp. 110-114."
    ),
    lifespan=lifespan,
)

app.include_router(queues.router, prefix="/queues", tags=["queues"])
app.include_router(history.router, prefix="/calculations", tags=["calculations"])


@app.get("/", tags=["system"], summary="API info")
def root() -> dict:
    """Return a short pointer to the docs and health endpoints."""
    return {
        "name": "Queueing Theory API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["system"], summary="Health check")
def health() -> dict:
    """Liveness probe."""
    return {"status": "ok"}
