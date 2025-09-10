from typing import Set
from fastapi import WebSocket

connections: Set[WebSocket] = set()

async def broadcast_json(payload: dict):
    dead = []
    for ws in list(connections):
        try:
            await ws.send_json(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        connections.discard(ws)
