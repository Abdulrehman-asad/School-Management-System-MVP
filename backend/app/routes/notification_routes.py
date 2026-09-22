"""
Routes for Notifications — the notification bell.

Every endpoint here is scoped to the logged-in user; there's no "view someone
else's notifications" mode, even for admins.

Includes a WebSocket endpoint (`/api/notifications/ws`) for real-time push:
when a notification is created for a connected user, it can be pushed
immediately instead of waiting for the next poll (see push_notification_event
in app/utils/ws_manager.py, called from notification_controller).
"""

from typing import List

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.auth.security import decode_token
from app.models.user import User
from app.controllers import notification_controller as crud
from app.schemas.notification import NotificationOut, UnreadCountOut, MarkAllReadOut
from app.utils.ws_manager import manager

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationOut])
def list_notifications(
    unread_only: bool = Query(False),
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.list_notifications(db, current_user.user_id, unread_only, skip, limit)


@router.get("/unread-count", response_model=UnreadCountOut)
def unread_count(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return UnreadCountOut(unread_count=crud.get_unread_count(db, current_user.user_id))


@router.put("/{notification_id}/read", response_model=NotificationOut)
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.mark_as_read(db, notification_id, current_user.user_id)


@router.put("/read-all", response_model=MarkAllReadOut)
def mark_all_as_read(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    count = crud.mark_all_as_read(db, current_user.user_id)
    return MarkAllReadOut(marked_count=count)


@router.delete("/{notification_id}", status_code=204)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    crud.delete_notification(db, notification_id, current_user.user_id)


# ---------------------------------------------------------------------
# WebSocket: real-time push
# ---------------------------------------------------------------------
@router.websocket("/ws")
async def notifications_websocket(websocket: WebSocket, token: str = Query(...)):
    """
    Connect with:  wss://<host>/api/notifications/ws?token=<access_token>

    Whenever a notification is created for this user elsewhere in the app
    (homework assigned, fee challan generated, notice posted, etc.), it is
    pushed here immediately as JSON matching NotificationOut's shape.
    """
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        await websocket.close(code=4401)
        return

    user_id = int(payload["sub"])
    await manager.connect(user_id, websocket)

    try:
        while True:
            # Clients don't need to send anything; this just keeps the connection open
            # and detects disconnects. Any received text is ignored.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
