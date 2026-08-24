import time
from typing import Dict, List, Any, Optional
from .entity_graph import EntityGraph

class TieredMemoryStore:
    """Three-tier memory store:
    1. Working Memory (Active task buffer)
    2. Episodic Memory (Timestamped dialogue history)
    3. Semantic / Entity Memory (Knowledge Graph)
    """
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.working_memory: Dict[str, Any] = {}
        self.episodic_memory: List[Dict[str, Any]] = []
        self.entity_graph = EntityGraph()

    def add_interaction(self, role: str, content: str):
        """Append interaction to episodic memory and extract entities."""
        entry = {
            "role": role,
            "content": content,
            "timestamp": time.time()
        }
        self.episodic_memory.append(entry)
        
        # If user message, extract entity facts
        if role == "user":
            self.entity_graph.extract_from_text(content)

    def set_working_context(self, key: str, value: Any):
        self.working_memory[key] = value

    def search_episodic(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Simple keyword/token overlap search across episodic memory."""
        q_tokens = set(query.lower().split())
        scored = []
        for item in self.episodic_memory:
            item_tokens = set(item["content"].lower().split())
            overlap = len(q_tokens.intersection(item_tokens))
            if overlap > 0:
                scored.append((overlap, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:top_k]]

    def consolidate(self) -> Dict[str, Any]:
        """Consolidate short-term episodic memory into durable user profile summaries."""
        total_msgs = len(self.episodic_memory)
        triples = self.entity_graph.all_triples()
        summary = f"User profile with {len(triples)} extracted entity facts from {total_msgs} interactions."
        self.set_working_context("user_profile_summary", summary)
        return {
            "consolidated_at": time.time(),
            "total_interactions": total_msgs,
            "entities_extracted": len(triples),
            "summary": summary
        }
