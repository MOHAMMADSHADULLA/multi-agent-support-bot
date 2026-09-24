from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_chat_endpoint_known_topic():
    resp = client.post("/chat", json={"message": "How do I cancel a booking?"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["route"] == "support"
    assert body["reply"]


def test_chat_endpoint_unknown_topic_escalates():
    resp = client.post("/chat", json={"message": "My spaceship warranty is void, help"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["route"] == "escalation"


def test_chat_endpoint_rejects_empty_body():
    resp = client.post("/chat", json={})
    assert resp.status_code == 422
