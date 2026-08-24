from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from .pipeline import MultiHopPipeline
from .compiler import TeleprompterOptimizer
from .metrics import EvaluationMetrics

app = FastAPI(
    title="DSPy Self-Improving Prompt Optimizer",
    version="1.0.0",
    description="Declarative prompt compilation and automated MIPROv2 teleprompter optimization"
)

pipeline = MultiHopPipeline()
optimizer = TeleprompterOptimizer(pipeline)

class PredictRequest(BaseModel):
    query: str
    context: Optional[str] = ""

class TrainExample(BaseModel):
    query: str
    ground_truth: str

class CompileRequest(BaseModel):
    train_set: List[TrainExample]
    max_demos: Optional[int] = 2

class EvaluateRequest(BaseModel):
    test_set: List[TrainExample]

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "active_instruction": pipeline.plan_sig.instruction,
        "compiled_demos": len(pipeline.plan_sig.demos)
    }

@app.post("/predict")
def predict(req: PredictRequest):
    return pipeline.forward(req.query, req.context or "")

@app.post("/compile")
def compile_prompts(req: CompileRequest):
    train_data = [{"query": t.query, "ground_truth": t.ground_truth} for t in req.train_set]
    result = optimizer.compile(train_data, max_bootstrapped_demos=req.max_demos or 2)
    return result

@app.post("/evaluate")
def evaluate(req: EvaluateRequest):
    results = []
    for item in req.test_set:
        out = pipeline.forward(item.query)
        f1 = EvaluationMetrics.token_f1_score(out["prediction"], item.ground_truth)
        compliance = EvaluationMetrics.format_compliance(out["prediction"])
        results.append({
            "query": item.query,
            "prediction": out["prediction"],
            "ground_truth": item.ground_truth,
            "token_f1": f1,
            "format_compliance": compliance
        })
    avg_f1 = sum(r["token_f1"] for r in results) / len(results) if results else 0.0
    return {
        "total_evaluated": len(results),
        "mean_token_f1": round(avg_f1, 4),
        "details": results
    }
