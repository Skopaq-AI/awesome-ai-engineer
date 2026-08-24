from typing import Dict, Any, List
from .memory_store import TieredMemoryStore

class StatefulAgent:
    """ReAct agent augmented with dynamic tiered memory lookup."""
    def __init__(self, memory: TieredMemoryStore):
        self.memory = memory

    def respond(self, user_input: str) -> Dict[str, Any]:
        # 1. Store user interaction
        self.memory.add_interaction("user", user_input)

        # 2. Retrieve relevant episodic memories
        relevant_memories = self.memory.search_episodic(user_input, top_k=2)

        # 3. Retrieve relevant entities from graph
        entities = self.memory.entity_graph.all_triples()

        # 4. Synthesize personalized response
        if entities and any(e["predicate"] in ["prefers", "location", "works_at"] for e in entities):
            fact_str = ", ".join([f"{e['predicate']}: {e['object']}" for e in entities])
            response_text = f"Based on your profile ({fact_str}), here is my tailored answer to: '{user_input}'"
        elif relevant_memories:
            response_text = f"Remembering our past conversation, here is my response to: '{user_input}'"
        else:
            response_text = f"I've noted this. Response to: '{user_input}'"

        # 5. Store assistant response
        self.memory.add_interaction("assistant", response_text)

        return {
            "response": response_text,
            "relevant_memories": relevant_memories,
            "extracted_entities": entities
        }
