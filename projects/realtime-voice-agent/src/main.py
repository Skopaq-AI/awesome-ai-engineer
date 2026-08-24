import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, Any, List
from .session import RealtimeSession
from .speech import AudioProcessor

app = FastAPI(
    title="Realtime Voice & Multimodal Agent",
    version="1.0.0",
    description="Sub-second bidirectional voice and multimodal streaming agent with tool interrupts"
)

active_sessions: Dict[str, RealtimeSession] = {}

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "active_sessions": len(active_sessions)
    }

@app.websocket("/ws/realtime/{session_id}")
async def websocket_realtime_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    session = active_sessions.setdefault(session_id, RealtimeSession(session_id))
    
    # Send connection ack
    await websocket.send_json({
        "type": "session.created",
        "session_id": session_id,
        "available_tools": session.tool_registry.list_tools()
    })

    try:
        while True:
            data = await websocket.receive_text()
            event = json.loads(data)
            event_type = event.get("type")

            if event_type == "input_audio_buffer.append":
                # Simulated audio chunk received
                raw_bytes = AudioProcessor.decode_chunk(event.get("audio", ""))
                is_speech, energy = AudioProcessor.detect_vad(raw_bytes)
                
                # If speech detected while synthesizing, interrupt!
                if is_speech and session.is_synthesizing:
                    interrupted = session.interrupt()
                    if interrupted:
                        await websocket.send_json({
                            "type": "response.interrupted",
                            "session_id": session_id
                        })

            elif event_type == "conversation.item.create":
                # Text or transcription turn
                user_text = event.get("item", {}).get("content", "")
                
                # Acknowledge user turn
                await websocket.send_json({
                    "type": "response.created",
                    "status": "in_progress"
                })
                
                session.is_synthesizing = True
                response_text = await session.process_user_turn(user_text)
                
                # Stream simulated audio chunks / text deltas
                words = response_text.split(" ")
                for i, word in enumerate(words):
                    await websocket.send_json({
                        "type": "response.audio_transcript.delta",
                        "delta": word + " ",
                        "index": i
                    })
                    await asyncio.sleep(0.01)

                session.is_synthesizing = False
                await websocket.send_json({
                    "type": "response.done",
                    "final_transcript": response_text
                })

    except WebSocketDisconnect:
        if session_id in active_sessions:
            del active_sessions[session_id]
