import time
from fastapi import FastAPI, HTTPException, Header, Request
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from .config import settings
from .cache import SemanticCache
from .limiter import TokenBucketRateLimiter
from .router import SmartRouter

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Production Enterprise AI Gateway with Smart Routing, Semantic Caching, and Fallback Cascades"
)

cache = SemanticCache(ttl_seconds=settings.cache_ttl_seconds)
rate_limiter = TokenBucketRateLimiter(rpm=settings.default_rate_limit_rpm, tpm=settings.default_token_limit_tpm)
router = SmartRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "auto"
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1024
    stream: Optional[bool] = False

class UsageInfo(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    routed_model: str
    cached: bool
    latency_ms: float
    choices: List[Dict[str, Any]]
    usage: UsageInfo

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "cache_stats": cache.stats()
    }

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(req: ChatCompletionRequest, x_api_key: Optional[str] = Header("default-client")):
    start_time = time.time()
    
    # 1. Rate Limiting Check
    allowed, reason = rate_limiter.check_and_consume(x_api_key, estimated_tokens=req.max_tokens or 100)
    if not allowed:
        raise HTTPException(status_code=429, detail=reason)
    
    # 2. Convert messages
    msg_dicts = [{"role": m.role, "content": m.content} for m in req.messages]
    
    # 3. Model Selection via Smart Router
    selected_model = router.select_model(req.model, msg_dicts)
    
    # 4. Check Semantic Cache
    if settings.enable_cache:
        cached_resp = cache.get(selected_model, msg_dicts, req.temperature or 0.7)
        if cached_resp:
            latency = (time.time() - start_time) * 1000.0
            cached_resp["cached"] = True
            cached_resp["latency_ms"] = round(latency, 2)
            return cached_resp

    # 5. Model Execution / Simulation with Fallback
    fallback_chain = router.get_fallback_chain(selected_model)
    response_content = None
    executed_model = selected_model
    
    for candidate_model in fallback_chain:
        try:
            # Simulate upstream LLM execution with deterministic output
            executed_model = candidate_model
            last_prompt = req.messages[-1].content if req.messages else ""
            response_content = f"[{executed_model} response to: '{last_prompt[:40]}...'] Processed via Enterprise AI Gateway."
            break
        except Exception:
            continue
            
    if not response_content:
        raise HTTPException(status_code=502, detail="All upstream models in fallback chain failed")

    # 6. Usage & Cost Estimation
    prompt_tokens = sum(len(m.content.split()) * 2 for m in req.messages)
    completion_tokens = len(response_content.split()) * 2
    total_tokens = prompt_tokens + completion_tokens
    cost = router.calculate_cost(executed_model, prompt_tokens, completion_tokens)
    latency = (time.time() - start_time) * 1000.0

    response_payload = {
        "id": f"chatcmpl-{int(time.time()*1000)}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": req.model or "auto",
        "routed_model": executed_model,
        "cached": False,
        "latency_ms": round(latency, 2),
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": response_content},
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": cost
        }
    }
    
    # 7. Store in Cache
    if settings.enable_cache:
        cache.set(selected_model, msg_dicts, req.temperature or 0.7, response_payload)

    return response_payload
