"""History endpoints: CRUD over saved calculations."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.calculator import compute_metrics
from app.db import get_db

router = APIRouter()


@router.post(
    "", response_model=schemas.CalculationOut, status_code=status.HTTP_201_CREATED,
    summary="Save a calculation",
)
def create_calculation(
    calc: schemas.CalculationCreate, db: Session = Depends(get_db)
) -> models.Calculation:
    """Compute the metrics for the given queue and persist them."""
    metrics = compute_metrics(calc.queue_type, calc.rho, calc.mu)
    row = models.Calculation(
        queue_type=calc.queue_type,
        rho=calc.rho,
        mu=calc.mu,
        E_N=metrics["E_N"],
        E_T=metrics["E_T"],
        E_W=metrics["E_W"],
        E_Q=metrics["E_Q"],
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get(
    "", response_model=list[schemas.CalculationOut],
    summary="List saved calculations",
)
def list_calculations(
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[models.Calculation]:
    """Return the most recent saved calculations, newest first."""
    return (
        db.query(models.Calculation)
        .order_by(models.Calculation.id.desc())
        .limit(limit)
        .all()
    )


@router.get(
    "/{calc_id}", response_model=schemas.CalculationOut,
    summary="Get one calculation",
)
def get_calculation(
    calc_id: int, db: Session = Depends(get_db)
) -> models.Calculation:
    """Return a single saved calculation by its id."""
    row = db.get(models.Calculation, calc_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return row


@router.delete(
    "/{calc_id}", status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a calculation",
)
def delete_calculation(calc_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a saved calculation by its id."""
    row = db.get(models.Calculation, calc_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    db.delete(row)
    db.commit()
