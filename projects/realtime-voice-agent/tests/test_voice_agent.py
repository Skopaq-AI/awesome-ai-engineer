import pytest
import base64
from fastapi.testclient import TestClient
from src.main import app
from src.speech import AudioProcessor
from src.session import RealtimeSession

client = TestClient(app)

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

def test_vad_audio_processor():
    # Silent frame
    silent_bytes = b"\x00\x00" * 100
    is_speech, energy = AudioProcessor.detect_vad(silent_bytes, threshold=100)
    assert not is_speech
    assert energy == 0.0

    # Loud frame
    loud_bytes = (1000).to_bytes(2, byteorder='little', signed=True) * 100
    is_speech, energy = AudioProcessor.detect_vad(loud_bytes, threshold=100)
    assert is_speech
    assert energy > 100

def test_websocket_realtime_turn():
    with client.websocket_connect("/ws/realtime/test-session-1") as ws:
        # 1. Receive session.created
        created = ws.receive_json()
        assert created["type"] == "session.created"
        assert "query_calendar" in created["available_tools"]

        # 2. Send conversation item (user asking calendar)
        ws.send_json({
            "type": "conversation.item.create",
            "item": {"content": "What is on my calendar today?"}
        })

        # 3. Receive in_progress
        in_prog = ws.receive_json()
        assert in_prog["type"] == "response.created"

        # 4. Receive stream deltas until response.done
        deltas = []
        while True:
            msg = ws.receive_json()
            if msg["type"] == "response.audio_transcript.delta":
                deltas.append(msg["delta"])
            elif msg["type"] == "response.done":
                assert "schedule" in msg["final_transcript"].lower()
                break
        assert len(deltas) > 0
