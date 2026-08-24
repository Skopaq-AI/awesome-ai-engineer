import hashlib
import time
from typing import Optional, Dict, Any

class SemanticCache:
    """High-performance in-memory semantic cache with TTL and metadata tracking."""
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl = ttl_seconds
        self._store: Dict[str, Dict[str, Any]] = {}
        self.hits: int = 0
        self.misses: int = 0

    def _generate_key(self, model: str, messages: list, temperature: float) -> str:
        serialized = f"{model}:{messages}:{temperature}"
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def get(self, model: str, messages: list, temperature: float) -> Optional[Dict[str, Any]]:
        key = self._generate_key(model, messages, temperature)
        entry = self._store.get(key)
        if not entry:
            self.misses += 1
            return None
        
        if time.time() - entry["timestamp"] > self.ttl:
            del self._store[key]
            self.misses += 1
            return None
        
        self.hits += 1
        return entry["response"]

    def set(self, model: str, messages: list, temperature: float, response: Dict[str, Any]) -> None:
        key = self._generate_key(model, messages, temperature)
        self._store[key] = {
            "response": response,
            "timestamp": time.time()
        }

    def clear(self) -> None:
        self._store.clear()
        self.hits = 0
        self.misses = 0

    def stats(self) -> Dict[str, Any]:
        total = self.hits + self.misses
        hit_rate = (self.hits / total) if total > 0 else 0.0
        return {
            "entries": len(self._store),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_pct": round(hit_rate * 100, 2)
        }
