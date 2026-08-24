import pytest
from fastapi.testclient import TestClient
from src.main import app, pipeline
from src.metrics import EvaluationMetrics

client = TestClient(app)

def test_metrics():
    score = EvaluationMetrics.token_f1_score("Answer: Modular pipeline architecture", "Answer: Modular pipeline architecture")
    assert score == 1.0

    score_partial = EvaluationMetrics.token_f1_score("Modular architecture", "Modular pipeline design")
    assert 0.0 < score_partial < 1.0

def test_pipeline_prediction():
    resp = client.post("/predict", json={"query": "How to scale vector search?"})
    assert resp.status_code == 200
    data = resp.json()
    assert "prediction" in data
    assert "plan_prompt" in data

def test_compile_teleprompter():
    train_set = [
        {"query": "How to design RAG?", "ground_truth": "Answer: Based on verified decomposition, the optimal approach to 'How to design RAG?' leverages modular pipeline design."},
        {"query": "How to route models?", "ground_truth": "Answer: Based on verified decomposition, the optimal approach to 'How to route models?' leverages modular pipeline design."}
    ]
    resp = client.post("/compile", json={"train_set": train_set, "max_demos": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "compiled"
    assert data["bootstrapped_demos_count"] == 2
    assert data["training_f1_score"] > 0.8

def test_evaluate():
    test_set = [
        {"query": "How to scale vector search?", "ground_truth": "Answer: Modular pipeline design."}
    ]
    resp = client.post("/evaluate", json={"test_set": test_set})
    assert resp.status_code == 200
    assert resp.json()["total_evaluated"] == 1
