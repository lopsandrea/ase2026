"""Real-time dashboard for task review and execution monitoring (paper §3.1).

A FastAPI + WebSocket app that streams Coordinator events to a single-page
client so QA engineers can review the auto-generated task list and watch
the Phase-3 execution loop in real time. Intentionally minimal — the
intended deployment is behind Wideverse's existing QA dashboard.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Doc2Test Dashboard", version="1.0")
_HERE = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(_HERE / "static")), name="static")

_clients: set[WebSocket] = set()


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return (_HERE / "templates" / "index.html").read_text()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.websocket("/ws")
async def ws(socket: WebSocket) -> None:
    await socket.accept()
    _clients.add(socket)
    try:
        while True:
            await socket.receive_text()
    except WebSocketDisconnect:
        _clients.discard(socket)


async def broadcast(event: dict) -> None:
    payload = json.dumps(event)
    for client in list(_clients):
        try:
            await client.send_text(payload)
        except Exception:
            _clients.discard(client)


def run() -> None:
    import uvicorn
    uvicorn.run("doc2test.ui.server:app", host="0.0.0.0", port=8080, log_level="info")


if __name__ == "__main__":
    run()
