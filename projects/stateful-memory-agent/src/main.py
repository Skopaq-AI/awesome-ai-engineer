from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from .memory_store import TieredMemoryStore
from .agent import StatefulAgent

app = FastAPI(
    title="Stateful Memory & Entity Agent",
    version="1.0.0",
    description="Tiered memory agent with working, episodic, and semantic knowledge graph recall"
)

user_stores: Dict[str, TieredMemoryStore] = {}

def get_or_create_store(user_id: str) -> TieredMemoryStore:
    if user_id not in user_stores:
        user_stores[user_id] = TieredMemoryStore(user_id)
    return user_stores[user_id]

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ConsolidateRequest(BaseModel):
    user_id: str

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "active_users": len(user_stores)
    }

@app.post("/chat")
def chat(req: ChatRequest):
    store = get_or_create_store(req.user_id)
    agent = StatefulAgent(store)
    return agent.respond(req.message)

@app.get("/memory/entities/{user_id}")
def get_entities(user_id: str):
    store = get_or_create_store(user_id)
    return {"user_id": user_id, "entities": store.entity_graph.all_triples()}

@app.get("/memory/episodic/{user_id}")
def get_episodic(user_id: str, query: Optional[str] = None):
    store = get_or_create_store(user_id)
    if query:
        return {"user_id": user_id, "results": store.search_episodic(query)}
    return {"user_id": user_id, "history": store.episodic_memory}

@app.post("/memory/consolidate")
def consolidate(req: ConsolidateRequest):
    store = get_or_create_store(req.user_id)
    return store.consolidate()
