import asyncio
import time
from typing import Dict, Any, List, Optional
from .tools import AgentToolRegistry
from .speech import AudioProcessor

class RealtimeSession:
    """Manages full-duplex voice streaming state, active turns, and interrupt handling."""
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.tool_registry = AgentToolRegistry()
        self.history: List[Dict[str, str]] = []
        self.is_synthesizing: bool = False
        self._current_turn_task: Optional[asyncio.Task] = None
        self.created_at = time.time()

    def interrupt(self) -> bool:
        """Interrupt active synthesis immediately upon user speech."""
        if self._current_turn_task and not self._current_turn_task.done():
            self._current_turn_task.cancel()
            self.is_synthesizing = False
            return True
        return False

    async def process_user_turn(self, user_transcript: str) -> str:
        """Generate response and execute tools if requested."""
        self.history.append({"role": "user", "content": user_transcript})
        
        # Check for tool intent
        if "calendar" in user_transcript.lower() or "schedule" in user_transcript.lower():
            tool_res = await self.tool_registry.execute("query_calendar", date="today")
            response = f"I checked your schedule: {tool_res}"
        elif "weather" in user_transcript.lower():
            tool_res = await self.tool_registry.execute("get_weather", location="San Francisco")
            response = f"The weather report is: {tool_res}"
        else:
            response = f"I understand: '{user_transcript}'. How else can I assist your workflow?"

        self.history.append({"role": "assistant", "content": response})
        return response
