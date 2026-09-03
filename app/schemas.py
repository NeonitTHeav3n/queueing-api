"""Pydantic schemas: request/response models with validation."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

QueueType = Literal["mm1", "md1"]


class QueueMetrics(BaseModel):
    """Steady-state performance metrics of a queueing system."""

    queue_type: QueueType
    rho: float
    mu: float
    E_N: float = Field(description="Mean number of jobs in the system")
    E_T: float = Field(description="Mean sojourn time")
    E_W: float = Field(description="Mean waiting time")
    E_Q: float = Field(description="Mean queue length")


class SimulationEstimate(BaseModel):
    """Monte-Carlo estimates of the performance metrics."""

    E_N: float
    E_T: float
    E_W: float
    E_Q: float
    n_departures: int


class SimulationRequest(BaseModel):
    """Request body for the simulation endpoint."""

    queue_type: QueueType = "mm1"
    rho: float = Field(gt=0.0, lt=1.0, examples=[0.7])
    mu: float = Field(default=1.0, gt=0.0)
    method: Literal["analytic", "simulation"] = "simulation"
    sim_time: float = Field(default=500.0, gt=0.0)
    seed: int = 42


class SimulationResponse(BaseModel):
    """Analytic results plus (optionally) Monte-Carlo estimates."""

    queue_type: QueueType
    rho: float
    mu: float
    method: Literal["analytic", "simulation"]
    analytic: QueueMetrics
    simulation: Optional[SimulationEstimate] = None
    elapsed_seconds: float


class CalculationCreate(BaseModel):
    """Request body to save a calculation into history."""

    queue_type: QueueType
    rho: float = Field(gt=0.0, lt=1.0, examples=[0.5])
    mu: float = Field(default=1.0, gt=0.0)


class CalculationOut(CalculationCreate):
    """Saved calculation, as returned by the history endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    E_N: float
    E_T: float
    E_W: float
    E_Q: float
    created_at: datetime
