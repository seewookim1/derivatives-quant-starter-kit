"""WebSocket 엔드포인트 핸들러"""

from __future__ import annotations

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect

from hdesk.api.websocket.manager import ConnectionManager

router = APIRouter(tags=["websocket"])


def get_ws_manager(request: Request) -> ConnectionManager:
    return request.app.state.ws_manager


@router.websocket("/ws/greeks")
async def ws_greeks(websocket: WebSocket) -> None:
    """실시간 Greeks 업데이트 스트림."""
    manager: ConnectionManager = websocket.app.state.ws_manager
    await manager.connect_greeks(websocket)
    try:
        while True:
            # 클라이언트 ping 수신 (연결 유지)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_greeks(websocket)


@router.websocket("/ws/pnl")
async def ws_pnl(websocket: WebSocket) -> None:
    """실시간 P&L 스트림."""
    manager: ConnectionManager = websocket.app.state.ws_manager
    await manager.connect_pnl(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_pnl(websocket)
