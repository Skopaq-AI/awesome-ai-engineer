import asyncio
from typing import Dict, Any, Callable

class AgentToolRegistry:
    """Registry of async agent tools with cancellation token support."""
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        async def query_calendar(date: str) -> str:
            await asyncio.sleep(0.05) # async simulated I/O
            return f"Schedule for {date}: 2 meetings (Design Review at 2 PM, 1:1 at 4 PM)"

        async def get_weather(location: str) -> str:
            await asyncio.sleep(0.05)
            return f"Current weather in {location}: 22°C, Partly Cloudy, 65% humidity"

        self.register("query_calendar", query_calendar)
        self.register("get_weather", get_weather)

    def register(self, name: str, fn: Callable):
        self._tools[name] = fn

    async def execute(self, tool_name: str, **kwargs) -> Any:
        if tool_name not in self._tools:
            return f"Error: Tool '{tool_name}' not found."
        return await self._tools[tool_name](**kwargs)

    def list_tools(self) -> list:
        return list(self._tools.keys())
