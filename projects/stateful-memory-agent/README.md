# Stateful Memory & Entity Agent

A stateful AI agent architecture implementing 3-tier memory management (Working Memory, Episodic History, and Semantic Knowledge Graph Triples) with automated memory consolidation.

## Architecture

- **Working Memory**: In-memory scratchpad for the immediate reasoning turn.
- **Episodic Memory**: Timestamped dialogue turns indexed for token-overlap and semantic recall.
- **Semantic / Entity Graph**: Knowledge graph triples (`subject`, `predicate`, `object`) extracted from conversational context.
- **Auto-Consolidation**: Background compaction pipeline summarizing dialogue into long-term persona facts.

## Quick Start

### Local Setup

```bash
# 1. Install dependencies
pip install -e ".[dev]"

# 2. Run agent server
uvicorn src.main:app --reload --port 8000

# 3. Execute tests
pytest tests/ -v
```

### Endpoints

- `POST /chat`: Interact with stateful agent and trigger automatic memory updates.
- `GET /memory/entities/{user_id}`: Retrieve knowledge graph triples for a user.
- `GET /memory/episodic/{user_id}?query=...`: Search past conversation turns.
- `POST /memory/consolidate`: Trigger background memory compaction.
