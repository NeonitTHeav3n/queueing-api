"""Tests for the history (CRUD) endpoints."""

import math


def test_create_and_get_calculation(client):
    resp = client.post("/calculations", json={"queue_type": "mm1", "rho": 0.5})
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == 1
    assert math.isclose(body["E_N"], 1.0)
    assert body["created_at"]

    resp = client.get(f"/calculations/{body['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == 1


def test_list_calculations(client):
    client.post("/calculations", json={"queue_type": "mm1", "rho": 0.3})
    client.post("/calculations", json={"queue_type": "md1", "rho": 0.8})
    resp = client.get("/calculations")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 2
    # newest first
    assert items[0]["rho"] == 0.8
    assert items[1]["rho"] == 0.3


def test_get_missing_calculation_returns_404(client):
    resp = client.get("/calculations/9999")
    assert resp.status_code == 404


def test_delete_calculation(client):
    created = client.post("/calculations", json={"queue_type": "md1", "rho": 0.4}).json()
    resp = client.delete(f"/calculations/{created['id']}")
    assert resp.status_code == 204
    resp = client.get(f"/calculations/{created['id']}")
    assert resp.status_code == 404


def test_create_rejects_invalid_rho(client):
    resp = client.post("/calculations", json={"queue_type": "mm1", "rho": 1.2})
    assert resp.status_code == 422
