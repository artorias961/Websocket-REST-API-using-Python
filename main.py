from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(
    title="WebSocket & REST API using Python",
    description="Integrated REST + WebSocket backend with shared state and broadcast updates.",
    version="1.0.0",
)

# -------------------------
# Shared State + WS Manager
# -------------------------
class ConnectionManager:
    def __init__(self) -> None:
        self._connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(websocket)

    async def broadcast(self, message: Dict[str, Any]) -> None:
        # Send to all currently connected websockets.
        async with self._lock:
            conns = list(self._connections)

        # Send outside lock to avoid blocking new connects.
        dead: list[WebSocket] = []
        for ws in conns:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)

        # Cleanup dead sockets
        if dead:
            async with self._lock:
                for ws in dead:
                    self._connections.discard(ws)

    async def count(self) -> int:
        async with self._lock:
            return len(self._connections)


manager = ConnectionManager()

# A minimal shared state model for "devices"
# device_id -> {"value": ..., "updated_at": ...}
STATE: Dict[str, Dict[str, Any]] = {}
STATE_LOCK = asyncio.Lock()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# -------------------------
# REST Models
# -------------------------
class DataUpdate(BaseModel):
    device_id: str = Field(..., min_length=1, description="Unique device/client identifier")
    value: Any = Field(..., description="Payload value (number/string/object)")


class ControlCommand(BaseModel):
    target: str = Field(..., min_length=1, description="Target device/client")
    command: str = Field(..., min_length=1, description="Command name")
    args: Optional[Dict[str, Any]] = Field(default=None, description="Optional command arguments")


# -------------------------
# REST Endpoints
# -------------------------
@app.get("/", response_class=HTMLResponse)
async def index():
    return """
<!DOCTYPE html>
<html>
<head>
  <title>WebSocket + REST API (Python)</title>
  <style>
    body {
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      padding: 40px;
      line-height: 1.6;
      background: #fafafa;
    }
    h1 { margin-bottom: 0; }
    h2 { margin-top: 28px; }
    .box {
      background: white;
      border: 1px solid #ddd;
      border-radius: 12px;
      padding: 24px;
      max-width: 820px;
    }
    ul { margin-top: 8px; }
    a {
      text-decoration: none;
      color: #1a73e8;
      font-weight: 500;
    }
    a:hover { text-decoration: underline; }
    .mono {
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      background: #f4f4f4;
      padding: 2px 6px;
      border-radius: 6px;
    }
    .note {
      background: #f7f9fc;
      border-left: 4px solid #4c6ef5;
      padding: 12px;
      margin-top: 12px;
    }
  </style>
</head>
<body>
  <div class="box">
    <h1>WebSocket & REST API using Python</h1>
    <p>
      This server demonstrates a backend that integrates
      <strong>RESTful APIs</strong> and <strong>WebSocket-based real-time communication</strong>.
    </p>

    <h2>🔗 REST API Interfaces</h2>
    <ul>
      <li><a href="/docs">📘 Swagger API Docs</a> — Interactive REST API testing</li>
      <li><a href="/redoc">📕 ReDoc API Docs</a> — Read-only API reference</li>
      <li><a href="/api/status">📊 API Status</a> — Live server & connection status</li>
      <li><a href="/api/data">📦 Current Device Data</a> — Shared system state</li>
    </ul>

    <h2>🔌 WebSocket Endpoint</h2>
    <p>
      <span class="mono">ws://127.0.0.1:8000/ws</span>
    </p>

    <h2>▶ How to Observe System Behavior</h2>
    <ul>
      <li>
        Run <span class="mono">device_one.py</span> →
        sends real-time telemetry via WebSocket
      </li>
      <li>
        Run <span class="mono">device_two.py</span> →
        sends REST data and control commands
      </li>
      <li>
        Open <span class="mono">dashboard.html</span> →
        observe live updates and events
      </li>
    </ul>

    <div class="note">
      <strong>Expected Result:</strong><br>
      As devices run, <span class="mono">/api/data</span> updates,
      <span class="mono">/api/status</span> changes, and the dashboard
      receives real-time WebSocket broadcasts.
    </div>
  </div>
</body>
</html>
"""

@app.get("/api/status")
async def status() -> Dict[str, Any]:
    async with STATE_LOCK:
        device_count = len(STATE)
    ws_count = await manager.count()
    return {
        "ok": True,
        "devices_known": device_count,
        "websocket_clients_connected": ws_count,
        "timestamp_utc": utc_now_iso(),
    }


@app.get("/api/data")
async def get_data() -> Dict[str, Any]:
    async with STATE_LOCK:
        snapshot = dict(STATE)
    return {
        "timestamp_utc": utc_now_iso(),
        "data": snapshot,
    }


@app.post("/api/data")
async def post_data(update: DataUpdate) -> Dict[str, Any]:
    # Update shared state
    async with STATE_LOCK:
        STATE[update.device_id] = {
            "value": update.value,
            "updated_at_utc": utc_now_iso(),
        }

    event = {
        "type": "data_update",
        "device_id": update.device_id,
        "value": update.value,
        "timestamp_utc": utc_now_iso(),
        "source": "rest",
    }
    # Broadcast to all WS clients
    await manager.broadcast(event)

    return {"ok": True, "stored": True, "event": event}


@app.post("/api/control")
async def control(cmd: ControlCommand) -> Dict[str, Any]:
    # In a real system you'd validate that target exists, permissions, etc.
    # Here we just broadcast a "control" event.
    event = {
        "type": "control",
        "target": cmd.target,
        "command": cmd.command,
        "args": cmd.args or {},
        "timestamp_utc": utc_now_iso(),
        "source": "rest",
    }
    await manager.broadcast(event)
    return {"ok": True, "dispatched": True, "event": event}


# -------------------------
# WebSocket Endpoint
# -------------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)

    # Send initial snapshot on connect
    async with STATE_LOCK:
        snapshot = dict(STATE)

    await websocket.send_json(
        {
            "type": "hello",
            "message": "connected",
            "timestamp_utc": utc_now_iso(),
            "data_snapshot": snapshot,
        }
    )

    try:
        while True:
            # Client can push events too
            msg = await websocket.receive_json()

            # Basic protocol:
            # {"type":"telemetry","device_id":"device_one","value":123}
            msg_type = msg.get("type")
            if msg_type == "telemetry":
                device_id = msg.get("device_id")
                if not device_id:
                    raise HTTPException(status_code=400, detail="telemetry missing device_id")

                value = msg.get("value")
                async with STATE_LOCK:
                    STATE[device_id] = {"value": value, "updated_at_utc": utc_now_iso()}

                event = {
                    "type": "data_update",
                    "device_id": device_id,
                    "value": value,
                    "timestamp_utc": utc_now_iso(),
                    "source": "websocket",
                }
                await manager.broadcast(event)

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong", "timestamp_utc": utc_now_iso()})
            
            elif msg_type == "control":
                event = {
                    "type": "control",
                    "target": msg.get("target"),
                    "command": msg.get("command"),
                    "args": msg.get("args") or {},
                    "timestamp_utc": utc_now_iso(),
                    "source": "websocket",
                }
                await manager.broadcast(event)


            else:
                # Unknown message type: echo it back for debugging
                await websocket.send_json(
                    {
                        "type": "echo",
                        "timestamp_utc": utc_now_iso(),
                        "received": msg,
                        "note": "Unrecognized message type",
                    }
                )

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception:
        # Ensure cleanup on unexpected errors
        await manager.disconnect(websocket)
        raise
