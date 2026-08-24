import re
from typing import Tuple, List

class PromptInjectionDetector:
    """Multi-layer prompt injection, jailbreak, and system override detector."""

    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
        r"disregard\s+(the\s+)?system\s+prompt",
        r"you\s+are\s+now\s+(DAN|unrestricted|in\s+developer\s+mode)",
        r"system\s*:\s*override",
        r"reveal\s+(your\s+)?(initial|hidden|system)\s+instructions",
        r"print\s+system\s+prompt",
        r"bypass\s+all\s+(safety|content)\s+filters"
    ]

    def __init__(self):
        self._compiled = [re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS]

    def scan(self, text: str) -> Tuple[bool, float, List[str]]:
        """Scan text for jailbreak and prompt injection patterns. Returns (is_flagged, risk_score, matched_patterns)."""
        matches = []
        for i, pattern in enumerate(self._compiled):
            if pattern.search(text):
                matches.append(self.INJECTION_PATTERNS[i])

        risk_score = min(1.0, len(matches) * 0.45)
        is_flagged = len(matches) > 0 or risk_score >= 0.4
        return is_flagged, round(risk_score, 2), matches
