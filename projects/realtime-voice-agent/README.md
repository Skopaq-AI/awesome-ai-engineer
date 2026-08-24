# Realtime Voice & Multimodal Streaming Agent

A sub-second latency bidirectional voice and multimodal agent built on WebSockets, chunked PCM audio framing, Voice Activity Detection (VAD), and cancelable async tool execution.

## Features

- **Full-Duplex Streaming**: Bidirectional WebSocket communication replicating the OpenAI Realtime API and Gemini Live protocol.
- **Voice Activity Detection (VAD)**: Real-time energy-based frame analysis for instant user speech detection.
- **Tool Interruption Protocol**: Gracefully and immediately aborts ongoing TTS/synthesis tasks whenever the user speaks.
- **Cancelable Async Tools**: Tool executions wrapped with cancellation tokens for safe interrupts.
- **Turn State Management**: Tracks active session history, speaker transitions, and latency metrics.

## Quick Start

### Local Setup

```bash
# 1. Install dependencies
pip install -e ".[dev]"

# 2. Run voice agent server
uvicorn src.main:app --reload --port 8000

# 3. Run test suite
pytest tests/ -v
```

### WebSocket Protocol

Connect via WebSocket to: `ws://localhost:8000/ws/realtime/{session_id}`
