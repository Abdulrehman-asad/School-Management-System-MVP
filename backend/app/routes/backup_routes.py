"""
Routes for Backup & Restore.

super_admin only (restore is destructive — wipes and reloads every table —
so it's deliberately more restricted than most admin actions).
"""

import json
from datetime import datetime

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import require_roles
from app.utils.backup_restore import export_backup, restore_backup

router = APIRouter(prefix="/api/backup", tags=["Backup & Restore"])

SUPER_ADMIN_ONLY = require_roles("super_admin")


@router.get("/export")
def export_database_backup(_=Depends(SUPER_ADMIN_ONLY)):
    buffer = export_backup()
    filename = f"shaheen_erp_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return StreamingResponse(
        buffer,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/restore")
async def restore_database_backup(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(SUPER_ADMIN_ONLY),
):
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Backup file must be a .json export from this system")

    try:
        contents = await file.read()
        backup_data = json.loads(contents)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Uploaded file is not valid JSON")

    try:
        row_counts = restore_backup(db, backup_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Restore failed and was rolled back: {e}")

    return {
        "message": "Database restored successfully. All data was replaced with the backup contents.",
        "tables_restored": row_counts,
        "total_rows": sum(row_counts.values()),
    }
