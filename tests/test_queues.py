"""Tests for the queue calculation endpoints."""

import math


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_root_points_to_docs(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["docs"] == "/docs"


def test_mm1_closed_form(client):
    resp = client.get("/queues/mm1", params={"rho": 0.5, "mu": 1.0})
    assert resp.status_code == 200
    body = resp.json()
    assert math.isclose(body["E_N"], 1.0)
    assert math.isclose(body["E_T"], 2.0)
    assert math.isclose(body["E_W"], 1.0)
    assert math.isclose(body["E_Q"], 0.5)


def test_md1_closed_form(client):
    resp = client.get("/queues/md1", params={"rho": 0.5, "mu": 1.0})
    assert resp.status_code == 200
    body = resp.json()
    assert math.isclose(body["E_N"], 0.75)
    assert math.isclose(body["E_T"], 1.5)
    assert math.isclose(body["E_W"], 0.5)
    assert math.isclose(body["E_Q"], 0.25)


def test_rho_must_be_below_one(client):
    resp = client.get("/queues/mm1", params={"rho": 1.0})
    assert resp.status_code == 422


def test_rho_must_be_positive(client):
    resp = client.get("/queues/mm1", params={"rho": 0.0})
    assert resp.status_code == 422


def test_mu_must_be_positive(client):
    resp = client.get("/queues/mm1", params={"rho": 0.5, "mu": 0.0})
    assert resp.status_code == 422


def test_missing_rho_is_rejected(client):
    resp = client.get("/queues/mm1")
    assert resp.status_code == 422


def test_simulate_analytic_only(client):
    resp = client.post(
        "/queues/simulate",
        json={"queue_type": "mm1", "rho": 0.7, "method": "analytic"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["simulation"] is None
    assert math.isclose(body["analytic"]["E_N"], 0.7 / 0.3)


def test_simulate_with_monte_carlo(client):
    resp = client.post(
        "/queues/simulate",
        json={"queue_type": "md1", "rho": 0.7, "method": "simulation", "seed": 42},
    )
    assert resp.status_code == 200
    body = resp.json()
    sim = body["simulation"]
    assert sim is not None
    assert sim["n_departures"] > 0
    assert sim["E_N"] > 0
    # Monte-Carlo estimate should be within a reasonable band of the theory.
    assert abs(sim["E_N"] - body["analytic"]["E_N"]) / body["analytic"]["E_N"] < 0.25


def test_simulate_rejects_unknown_queue(client):
    resp = client.post(
        "/queues/simulate", json={"queue_type": "mg1", "rho": 0.5}
    )
    assert resp.status_code == 422
