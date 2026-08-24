from typing import Dict, Any

class EvaluationMetrics:
    """Evaluation metrics for declarative prompt outputs."""

    @staticmethod
    def token_f1_score(prediction: str, ground_truth: str) -> float:
        pred_tokens = set(prediction.lower().split())
        truth_tokens = set(ground_truth.lower().split())
        if not pred_tokens or not truth_tokens:
            return 1.0 if pred_tokens == truth_tokens else 0.0
        
        common = pred_tokens.intersection(truth_tokens)
        if not common:
            return 0.0
        
        precision = len(common) / len(pred_tokens)
        recall = len(common) / len(truth_tokens)
        f1 = 2 * (precision * recall) / (precision + recall)
        return round(f1, 4)

    @staticmethod
    def format_compliance(prediction: str, required_prefix: str = "Answer:") -> float:
        return 1.0 if prediction.strip().startswith(required_prefix) else 0.5
