import copy
from typing import List, Dict, Any
from .pipeline import MultiHopPipeline
from .metrics import EvaluationMetrics

class TeleprompterOptimizer:
    """MIPROv2-style teleprompter optimizer searching over instruction proposals and few-shot boots."""
    
    CANDIDATE_INSTRUCTIONS = [
        "Decompose input rigorously into independent sub-queries, then synthesize with exact evidence.",
        "Perform structured multi-step reasoning, validating constraints at each step.",
        "Generate a step-by-step verification plan followed by an authoritative architectural conclusion."
    ]

    def __init__(self, pipeline: MultiHopPipeline):
        self.pipeline = pipeline

    def compile(self, train_set: List[Dict[str, str]], max_bootstrapped_demos: int = 2) -> Dict[str, Any]:
        """Compile and optimize pipeline prompt instructions and few-shot examples."""
        best_score = -1.0
        best_instruction = self.pipeline.plan_sig.instruction
        best_demos = []

        # 1. Bootstrap candidate demonstrations
        bootstrapped = []
        for example in train_set[:max_bootstrapped_demos]:
            bootstrapped.append({
                "query": example.get("query", ""),
                "sub_questions": f"1. Analyze '{example.get('query', '')}'",
                "Answer": example.get("ground_truth", "")
            })

        # 2. Search over candidate instructions
        for candidate in self.CANDIDATE_INSTRUCTIONS:
            test_pipe = copy.deepcopy(self.pipeline)
            test_pipe.plan_sig.instruction = candidate
            test_pipe.plan_sig.demos = bootstrapped
            
            # Evaluate across train set
            scores = []
            for item in train_set:
                output = test_pipe.forward(item["query"])
                f1 = EvaluationMetrics.token_f1_score(output["prediction"], item["ground_truth"])
                scores.append(f1)
                
            avg_score = sum(scores) / len(scores) if scores else 0.0
            if avg_score > best_score:
                best_score = avg_score
                best_instruction = candidate
                best_demos = bootstrapped

        # Apply optimal instruction and demos to active pipeline
        self.pipeline.plan_sig.instruction = best_instruction
        self.pipeline.plan_sig.demos = best_demos

        return {
            "status": "compiled",
            "optimized_instruction": best_instruction,
            "bootstrapped_demos_count": len(best_demos),
            "training_f1_score": round(best_score, 4)
        }
