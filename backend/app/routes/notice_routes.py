"""
Routes for the Notice Board.

Create/update/delete: admin, super_admin only.
Read: any authenticated user — GET /api/notices returns only notices relevant
to that user's role/class by default (pass all=true to see everything, admin only).
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models.user import User
from app.models.notice import NoticeAudience
from app.controllers import notice_controller as crud
from app.schemas.notice import NoticeCreate, NoticeUpdate, NoticeOut

router = APIRouter(prefix="/api/notices", tags=["Notice Board"])

ADMIN_ONLY = require_roles("admin", "super_admin")


@router.post("", response_model=NoticeOut, status_code=201)
def create_notice(
    payload: NoticeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(ADMIN_ONLY),
):
    return crud.create_notice(db, payload, current_user.user_id)


@router.get("", response_model=List[NoticeOut])
def list_notices(
    show_all: bool = Query(False, description="Admins only: bypass role-based filtering"),
    audience: Optional[NoticeAudience] = Query(None),
    class_id: Optional[int] = Query(None),
    active_only: bool = Query(True),
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if show_all:
        if current_user.role.role_name not in ("admin", "super_admin"):
            raise HTTPException(status_code=403, detail="Only admins can bypass role-based filtering")
        return crud.list_notices(db, audience, class_id, active_only, skip, limit)

    return crud.list_notices_for_user(db, current_user, skip, limit)


@router.get("/{notice_id}", response_model=NoticeOut)
def get_notice(notice_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return crud.get_notice(db, notice_id)


@router.put("/{notice_id}", response_model=NoticeOut)
def update_notice(notice_id: int, payload: NoticeUpdate, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    return crud.update_notice(db, notice_id, payload)


@router.delete("/{notice_id}", status_code=204)
def delete_notice(notice_id: int, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    crud.delete_notice(db, notice_id)
