"""
WebSocket connection manager for real-time notification push.

FastAPI route handlers defined with `def` (not `async def`) run in a worker
thread, not the event loop — so controller code can't just `await` a websocket
send. `push_to_user_threadsafe` bridges that gap using
`asyncio.run_coroutine_threadsafe`, scheduling the send back onto the main
event loop captured at app startup.
"""

import asyncio
from typing import Dict, List, Optional

from fastapi import WebSocket


class ConnectionManager:
    """Tracks active WebSocket connections, keyed by user_id (a user may have
    multiple tabs/devices open at once, so each user_id maps to a list)."""

    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.main_loop: Optional[asyncio.AbstractEventLoop] = None

    def set_main_loop(self, loop: asyncio.AbstractEventLoop):
        self.main_loop = loop

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(user_id, []).append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        connections = self.active_connections.get(user_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections and user_id in self.active_connections:
            del self.active_connections[user_id]

    async def push_to_user(self, user_id: int, payload: dict):
        for connection in list(self.active_connections.get(user_id, [])):
            try:
                await connection.send_json(payload)
            except Exception:
                # Connection likely dropped; clean it up rather than letting it linger
                self.disconnect(user_id, connection)

    def push_to_user_threadsafe(self, user_id: int, payload: dict):
        """Call this from synchronous controller code (regular `def` routes)."""
        if self.main_loop is None:
            return  # no event loop captured yet (e.g. during tests) — silently skip
        if user_id not in self.active_connections:
            return  # nobody connected for this user — nothing to push
        asyncio.run_coroutine_threadsafe(self.push_to_user(user_id, payload), self.main_loop)


manager = ConnectionManager()
