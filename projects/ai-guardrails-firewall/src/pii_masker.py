import re
from typing import Tuple, Dict, List

class PIIMasker:
    """Detects and redacts Personally Identifiable Information (PII) and secret keys."""

    PATTERNS = {
        "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "PHONE": r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
        "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
        "CREDIT_CARD": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        "API_KEY": r"(?:sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{20,}|xoxb-[a-zA-Z0-9]{10,})"
    }

    def __init__(self):
        self._compiled = {k: re.compile(v) for k, v in self.PATTERNS.items()}

    def mask(self, text: str) -> Tuple[str, Dict[str, int]]:
        """Redacts PII and returns masked text along with count of redacted entities."""
        redacted_text = text
        stats = {}
        
        for pii_type, pattern in self._compiled.items():
            matches = pattern.findall(redacted_text)
            if matches:
                stats[pii_type] = len(matches)
                redacted_text = pattern.sub(f"[REDACTED_{pii_type}]", redacted_text)
                
        return redacted_text, stats
