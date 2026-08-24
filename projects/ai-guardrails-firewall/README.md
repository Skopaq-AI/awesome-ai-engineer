# AI Guardrails & Security Firewall

A zero-trust GenAI runtime security firewall providing multi-stage prompt injection detection, PII/secret data masking, JSON schema auto-remediation, and toxic output moderation.

## Core Capabilities

- **Prompt Injection & Jailbreak Defense**: Analyzes prompt tokens for DAN patterns, system prompt overrides, and adversarial delimiter bypasses.
- **PII & Secret Key Redaction**: High-speed regex and token filtering for Emails, Phone Numbers, SSNs, Credit Cards, and API Keys (`sk-...`, `ghp_...`).
- **Structured Schema Auto-Remediation**: Validates LLM responses against expected JSON schemas, strips markdown fences, and repairs common syntax errors.
- **Pre & Post-Generation Hooks**: Drop-in middleware for REST and WebSocket pipelines.

## Quick Start

### Local Setup

```bash
# 1. Install dependencies
pip install -e ".[dev]"

# 2. Run guardrails server
uvicorn src.main:app --reload --port 8000

# 3. Run test suite
pytest tests/ -v
```

### Endpoints

- `POST /v1/guard/validate-input`: Scan user prompt for injection risks and redact PII.
- `POST /v1/guard/validate-output`: Verify output structure, detect secret leaks, and validate schemas.
