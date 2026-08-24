import pytest
from fastapi.testclient import TestClient
from src.main import app, cache, rate_limiter

client = TestClient(app)

def setup_function():
    cache.clear()

def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "cache_stats" in data

def test_chat_completions_auto_routing_fast():
    payload = {
        "model": "auto",
        "messages": [
            {"role": "user", "content": "Hello, how are you today?"}
        ]
    }
    resp = client.post("/v1/chat/completions", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["routed_model"] == "gpt-4o-mini"
    assert data["cached"] is False
    assert len(data["choices"]) > 0
    assert "usage" in data

def test_chat_completions_auto_routing_reasoning():
    payload = {
        "model": "auto",
        "messages": [
            {"role": "user", "content": "Please derive step-by-step and prove the correctness of the distributed consensus algorithm."}
        ]
    }
    resp = client.post("/v1/chat/completions", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["routed_model"] == "deepseek-r1"

def test_semantic_cache_hit():
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Cache test message"}],
        "temperature": 0.0
    }
    # 1st request -> Miss
    resp1 = client.post("/v1/chat/completions", json=payload)
    assert resp1.status_code == 200
    assert resp1.json()["cached"] is False
    
    # 2nd request -> Hit
    resp2 = client.post("/v1/chat/completions", json=payload)
    assert resp2.status_code == 200
    assert resp2.json()["cached"] is True
