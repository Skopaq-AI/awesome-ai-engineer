# Enterprise AI Gateway & Cost Router

A production-grade, resilient AI Gateway implementing complexity classification, cost-effective model routing (RouteLLM paradigm), semantic caching, token-bucket rate limiting, and automated multi-provider fallback cascades.

## Features

- **OpenAI-Compatible API**: Drop-in `/v1/chat/completions` endpoint for any LLM client.
- **Smart Complexity Routing**: Dynamically classifies prompts to Fast (`gpt-4o-mini`), Strong (`gpt-4o`), or Reasoning (`deepseek-r1`) models to slash inference costs.
- **Semantic Caching**: In-memory and Redis-ready cache layer with sub-millisecond response latency for repeated queries.
- **Token-Bucket Rate Limiter**: Per-client tracking of Requests Per Minute (RPM) and Tokens Per Minute (TPM).
- **Fallback Cascades**: Automatic retry across secondary and tertiary models upon upstream failure or rate limit.
- **Cost & Latency Telemetry**: Real-time USD spend estimation per prompt/completion pair.

## Quick Start

### Local Setup

```bash
# 1. Install dependencies
pip install -e ".[dev]"

# 2. Run gateway server
uvicorn src.main:app --reload --port 8000

# 3. Execute test suite
pytest tests/ -v
```

### Docker Setup

```bash
docker compose up --build
```

## API Usage

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: client-123" \
  -d '{
    "model": "auto",
    "messages": [
      {"role": "user", "content": "Explain Kubernetes architecture step-by-step"}
    ]
  }'
```
