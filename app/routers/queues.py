"""Queue calculation endpoints: closed-form and simulation."""

from __future__ import annotations

import time

from fastapi import APIRouter, Query

from app.calculator import compute_metrics, simulate_queue
from app.schemas import (
    QueueMetrics,
    SimulationRequest,
    SimulationResponse,
)

router = APIRouter()


def _metrics(queue_type: str, rho: float, mu: float) -> QueueMetrics:
    metrics = compute_metrics(queue_type, rho, mu)
    return QueueMetrics(
        queue_type=queue_type, rho=rho, mu=mu,
        E_N=metrics["E_N"], E_T=metrics["E_T"],
        E_W=metrics["E_W"], E_Q=metrics["E_Q"],
    )


@router.get("/mm1", response_model=QueueMetrics, summary="M/M/1 closed-form metrics")
def mm1(
    rho: float = Query(gt=0.0, lt=1.0, description="Load 0 < rho < 1"),
    mu: float = Query(default=1.0, gt=0.0, description="Service rate"),
) -> QueueMetrics:
    """Return the steady-state metrics of an M/M/1 queue for a given load."""
    return _metrics("mm1", rho, mu)


@router.get("/md1", response_model=QueueMetrics, summary="M/D/1 closed-form metrics")
def md1(
    rho: float = Query(gt=0.0, lt=1.0, description="Load 0 < rho < 1"),
    mu: float = Query(default=1.0, gt=0.0, description="Service rate"),
) -> QueueMetrics:
    """Return the steady-state metrics of an M/D/1 queue for a given load."""
    return _metrics("md1", rho, mu)


@router.post("/simulate", response_model=SimulationResponse, summary="Analytic + Monte-Carlo")
def simulate(req: SimulationRequest) -> SimulationResponse:
    """Compute closed-form metrics and, optionally, Monte-Carlo estimates."""
    start = time.perf_counter()
    analytic = _metrics(req.queue_type, req.rho, req.mu)

    estimate = None
    if req.method == "simulation":
        sim = simulate_queue(
            req.queue_type, req.rho, req.mu, req.sim_time, req.seed
        )
        estimate = sim

    elapsed = time.perf_counter() - start
    return SimulationResponse(
        queue_type=req.queue_type,
        rho=req.rho,
        mu=req.mu,
        method=req.method,
        analytic=analytic,
        simulation=estimate,
        elapsed_seconds=round(elapsed, 4),
    )
