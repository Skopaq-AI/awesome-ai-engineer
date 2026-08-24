import pytest
from fastapi.testclient import TestClient
from src.main import app, user_stores

client = TestClient(app)

def setup_function():
    user_stores.clear()

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

def test_entity_extraction_and_chat():
    # 1. User shares preference
    req1 = {"user_id": "user-42", "message": "I prefer python over typescript"}
    resp1 = client.post("/chat", json=req1)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert len(data1["extracted_entities"]) > 0

    # 2. Check entities endpoint
    resp2 = client.get("/memory/entities/user-42")
    assert resp2.status_code == 200
    entities = resp2.json()["entities"]
    assert any(e["predicate"] == "prefers" and e["object"] == "python" for e in entities)

    # 3. Follow-up query utilizes entity profile
    req3 = {"user_id": "user-42", "message": "Recommend me a coding framework"}
    resp3 = client.post("/chat", json=req3)
    assert resp3.status_code == 200
    assert "prefers" in resp3.json()["response"]

def test_consolidation():
    req = {"user_id": "user-42", "message": "I live in Seattle"}
    client.post("/chat", json=req)
    
    cons_resp = client.post("/memory/consolidate", json={"user_id": "user-42"})
    assert cons_resp.status_code == 200
    assert cons_resp.json()["total_interactions"] >= 2
