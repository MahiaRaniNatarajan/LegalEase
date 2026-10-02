"""Member 5: integration tests."""
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health():
    assert client.get("/").json() == {"status": "ok"}


def test_simplify():
    r = client.post("/simplify", json={"text": "hereinafter the lessee"})
    assert r.status_code == 200
    assert "result" in r.json()
