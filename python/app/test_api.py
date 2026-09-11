import pytest
from fastapi.testclient import TestClient
from python.app.main import app
from python.app.data import data_loaded

client = TestClient(app)

needs_data = pytest.mark.skipif(not data_loaded(), reason="output files not present")

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] in ("ok", "degraded")

@needs_data
def test_months_returns_list():
    r = client.get("/api/months")
    assert r.status_code == 200
    months = r.json()["available_months"]
    assert len(months) > 0
    assert all(len(m) == 7 for m in months)

@needs_data
def test_tracts_returns_ranked_list():
    months = client.get("/api/months").json()["available_months"]
    r = client.get("/api/tracts", params={"month": months[0], "top_n": 5})
    assert r.status_code == 200
    body = r.json()
    assert len(body["tracts"]) <= 5
    assert body["kpi"]["top_n"] == 5

@needs_data
def test_equity_returns_groups():
    months = client.get("/api/months").json()["available_months"]
    r = client.get("/api/equity", params={"month": months[0]})
    assert r.status_code == 200
    body = r.json()
    assert len(body["groups"]) > 0
    assert "passed" in body

def test_campaign_returns_202():
    r = client.post("/api/campaign", json={"month": "2024-06", "top_n": 10})
    assert r.status_code == 202
    body = r.json()
    assert body["status"] == "started"
    assert "campaign_2024_06" in body["job_id"]
