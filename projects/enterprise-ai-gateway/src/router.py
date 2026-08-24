import time
from typing import Dict, List, Any, Optional
from .config import settings

class SmartRouter:
    """Intelligent model router implementing complexity classification, cost routing, and fallback cascades."""
    
    def __init__(self):
        self.routing_rules = {
            "fast": settings.fast_model,
            "strong": settings.strong_model,
            "reasoning": settings.reasoning_model
        }
        self.fallbacks = {
            "gpt-4o": ["claude-3-5-sonnet", "deepseek-r1", "gpt-4o-mini"],
            "claude-3-5-sonnet": ["gpt-4o", "deepseek-r1", "gpt-4o-mini"],
            "deepseek-r1": ["gpt-4o", "claude-3-5-sonnet", "gpt-4o-mini"],
            "gpt-4o-mini": ["gemma-2-9b"]
        }

    def classify_complexity(self, messages: List[Dict[str, str]]) -> str:
        """Classify prompt complexity to determine whether to route to Fast, Strong, or Reasoning model."""
        full_text = " ".join([m.get("content", "") for m in messages])
        total_len = len(full_text)
        
        # Heuristics for reasoning / complex prompts
        reasoning_keywords = ["prove", "derive", "step-by-step", "code architecture", "analyze complexity", "theorem", "root cause"]
        if any(kw in full_text.lower() for kw in reasoning_keywords) or total_len > 4000:
            return "reasoning"
        elif total_len > 1200 or len(messages) > 6:
            return "strong"
        else:
            return "fast"

    def select_model(self, requested_model: Optional[str], messages: List[Dict[str, str]]) -> str:
        if requested_model and requested_model != "auto":
            return requested_model
        complexity = self.classify_complexity(messages)
        return self.routing_rules.get(complexity, settings.fast_model)

    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        pricing = settings.model_pricing.get(model, {"prompt": 0.50, "completion": 1.50})
        prompt_cost = (prompt_tokens / 1_000_000.0) * pricing["prompt"]
        completion_cost = (completion_tokens / 1_000_000.0) * pricing["completion"]
        return round(prompt_cost + completion_cost, 6)

    def get_fallback_chain(self, primary_model: str) -> List[str]:
        return [primary_model] + self.fallbacks.get(primary_model, [settings.fast_model])
