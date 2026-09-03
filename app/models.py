"""ORM models."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Calculation(Base):
    """A saved queueing-metrics calculation (history entry)."""

    __tablename__ = "calculations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    queue_type: Mapped[str] = mapped_column(String(8))  # "mm1" | "md1"
    rho: Mapped[float] = mapped_column(Float)
    mu: Mapped[float] = mapped_column(Float)

    E_N: Mapped[float] = mapped_column(Float)
    E_T: Mapped[float] = mapped_column(Float)
    E_W: Mapped[float] = mapped_column(Float)
    E_Q: Mapped[float] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
