import time
from typing import Dict, Tuple

class TokenBucketRateLimiter:
    """Token-bucket rate limiter tracking both Requests Per Minute (RPM) and Tokens Per Minute (TPM)."""
    def __init__(self, rpm: int = 600, tpm: int = 100000):
        self.rpm = rpm
        self.tpm = tpm
        self._clients: Dict[str, Dict[str, float]] = {}

    def check_and_consume(self, client_id: str, estimated_tokens: int = 100) -> Tuple[bool, str]:
        now = time.time()
        client = self._clients.setdefault(client_id, {
            "req_tokens": float(self.rpm),
            "tok_tokens": float(self.tpm),
            "last_update": now
        })
        
        # Refill tokens based on elapsed time
        elapsed = now - client["last_update"]
        client["last_update"] = now
        
        # Refill rates per second
        client["req_tokens"] = min(float(self.rpm), client["req_tokens"] + elapsed * (self.rpm / 60.0))
        client["tok_tokens"] = min(float(self.tpm), client["tok_tokens"] + elapsed * (self.tpm / 60.0))
        
        # Check capacity
        if client["req_tokens"] < 1.0:
            return False, "Rate limit exceeded (Requests Per Minute)"
        if client["tok_tokens"] < estimated_tokens:
            return False, "Rate limit exceeded (Tokens Per Minute)"
            
        # Consume
        client["req_tokens"] -= 1.0
        client["tok_tokens"] -= estimated_tokens
        return True, "OK"
