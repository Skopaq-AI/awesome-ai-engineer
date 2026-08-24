import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from .injection_detector import PromptInjectionDetector
from .pii_masker import PIIMasker
from .schema_guard import SchemaGuard

app = FastAPI(
    title="AI Guardrails & Security Firewall",
    version="1.0.0",
    description="Zero-trust GenAI runtime security firewall, prompt injection defense, and PII redaction"
)

detector = PromptInjectionDetector()
masker = PIIMasker()

class InputValidationRequest(BaseModel):
    prompt: str
    mask_pii: Optional[bool] = True
    block_injection: Optional[bool] = True

class InputValidationResponse(BaseModel):
    passed: bool
    sanitized_prompt: str
    injection_flagged: bool
    risk_score: float
    matched_injection_patterns: List[str]
    redacted_pii: Dict[str, int]

class OutputValidationRequest(BaseModel):
    raw_output: str
    required_keys: Optional[List[str]] = None

class OutputValidationResponse(BaseModel):
    passed: bool
    status: str
    parsed_json: Optional[Dict[str, Any]] = None
    redacted_output: str
    leaked_secrets: Dict[str, int]

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "guardrails": ["prompt_injection", "pii_redaction", "schema_validation", "secret_leak_filter"]
    }

@app.post("/v1/guard/validate-input", response_model=InputValidationResponse)
def validate_input(req: InputValidationRequest):
    # 1. Prompt Injection Scan
    is_injection, risk_score, patterns = detector.scan(req.prompt)
    
    if is_injection and req.block_injection:
        return InputValidationResponse(
            passed=False,
            sanitized_prompt=req.prompt,
            injection_flagged=True,
            risk_score=risk_score,
            matched_injection_patterns=patterns,
            redacted_pii={}
        )

    # 2. PII Masking
    sanitized, pii_stats = masker.mask(req.prompt) if req.mask_pii else (req.prompt, {})
    
    return InputValidationResponse(
        passed=True,
        sanitized_prompt=sanitized,
        injection_flagged=False,
        risk_score=risk_score,
        matched_injection_patterns=patterns,
        redacted_pii=pii_stats
    )

@app.post("/v1/guard/validate-output", response_model=OutputValidationResponse)
def validate_output(req: OutputValidationRequest):
    # 1. Secret / PII Leak Check
    sanitized, pii_stats = masker.mask(req.raw_output)

    # 2. Schema check if required_keys provided
    if req.required_keys:
        valid, parsed, msg = SchemaGuard.validate_and_repair_json(sanitized, req.required_keys)
        return OutputValidationResponse(
            passed=valid,
            status=msg,
            parsed_json=parsed,
            redacted_output=sanitized,
            leaked_secrets=pii_stats
        )

    return OutputValidationResponse(
        passed=True,
        status="Passed output validation",
        parsed_json=None,
        redacted_output=sanitized,
        leaked_secrets=pii_stats
    )
