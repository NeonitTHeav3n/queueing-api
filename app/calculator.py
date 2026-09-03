"""Queueing-theory calculations: closed-form formulas and simulation.

Formulas follow Bocharov & Pechinkin, "Queueing Theory", pp. 110-114.
"""

from __future__ import annotations

import numpy as np

# --------------------------------------------------------------------------
# Closed-form (analytic) results
# --------------------------------------------------------------------------


def mm1_metrics(rho: float, mu: float = 1.0) -> dict:
    """Steady-state metrics of the M/M/1 queue.

    E[N] = rho / (1 - rho)
    E[T] = 1 / (mu * (1 - rho))
    E[W] = rho / (mu * (1 - rho))
    E[Q] = rho^2 / (1 - rho)
    """
    lam = rho * mu
    return {
        "E_N": rho / (1.0 - rho),
        "E_T": 1.0 / (mu * (1.0 - rho)),
        "E_W": rho / (mu * (1.0 - rho)),
        "E_Q": rho ** 2 / (1.0 - rho),
        # keep lam for reference in simulation helpers
        "_lam": lam,
    }


def md1_metrics(rho: float, mu: float = 1.0) -> dict:
    """Steady-state metrics of the M/D/1 queue (deterministic service).

    E[N] = rho + rho^2 / (2 (1 - rho))
    E[T] = (2 - rho) / (2 mu (1 - rho))
    E[W] = rho / (2 mu (1 - rho))
    E[Q] = rho^2 / (2 (1 - rho))
    """
    lam = rho * mu
    return {
        "E_N": rho + rho ** 2 / (2.0 * (1.0 - rho)),
        "E_T": (2.0 - rho) / (2.0 * mu * (1.0 - rho)),
        "E_W": rho / (2.0 * mu * (1.0 - rho)),
        "E_Q": rho ** 2 / (2.0 * (1.0 - rho)),
        "_lam": lam,
    }


def compute_metrics(queue_type: str, rho: float, mu: float = 1.0) -> dict:
    """Dispatch to the right closed-form model."""
    if queue_type == "mm1":
        return mm1_metrics(rho, mu)
    if queue_type == "md1":
        return md1_metrics(rho, mu)
    raise ValueError(f"Unknown queue type: {queue_type!r}")


# --------------------------------------------------------------------------
# Monte-Carlo simulation (fast, vectorized, deterministic given a seed)
# --------------------------------------------------------------------------


def simulate_queue(
    queue_type: str, rho: float, mu: float = 1.0, sim_time: float = 500.0, seed: int = 42
) -> dict:
    """Estimate E[N] / E[T] / E[W] / E[Q] by simulating a single long run.

    Inter-arrival times are exponential; service times are exponential
    (M/M/1) or constant 1/mu (M/D/1). Uses Little's law for E[Q] and E[W].
    """
    lam = rho * mu
    rng = np.random.default_rng(seed)

    n = int(2.0 * lam * sim_time) + 1000
    interarrivals = rng.exponential(1.0 / lam, size=n)
    arrivals = np.cumsum(interarrivals)
    arrivals = arrivals[arrivals <= sim_time]

    if len(arrivals) == 0:
        return {"E_N": 0.0, "E_T": 0.0, "E_W": 0.0, "E_Q": 0.0, "n_departures": 0}

    if queue_type == "mm1":
        services = rng.exponential(1.0 / mu, size=len(arrivals))
    else:  # md1
        services = np.full(len(arrivals), 1.0 / mu)

    departures = np.empty_like(arrivals)
    departures[0] = arrivals[0] + services[0]
    for i in range(1, len(arrivals)):
        departures[i] = max(arrivals[i], departures[i - 1]) + services[i]

    mask = departures <= sim_time
    if not mask.any():
        return {"E_N": 0.0, "E_T": 0.0, "E_W": 0.0, "E_Q": 0.0, "n_departures": 0}

    time_in_system = departures[mask] - arrivals[mask]
    E_T = float(np.mean(time_in_system))
    E_N = float(lam * E_T)  # Little's law
    E_W = max(0.0, E_T - 1.0 / mu)
    E_Q = float(lam * E_W)

    return {
        "E_N": E_N,
        "E_T": E_T,
        "E_W": E_W,
        "E_Q": E_Q,
        "n_departures": int(mask.sum()),
    }
