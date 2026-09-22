"""
Shaheen Model Girls High School ERP - FastAPI Entry Point

Run locally with:
    uvicorn app.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import settings
import app.models  # noqa: F401  (registers all ORM models before routes touch the DB)
from app.routes import (
    auth_routes, academic_routes, teacher_routes, student_routes,
    attendance_routes, homework_routes, timetable_routes,
    exam_routes, result_routes, fee_routes,
    notice_routes, notification_routes, report_routes,
    upload_routes, backup_routes,
)
from app.utils.ws_manager import manager

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for the Shaheen Model Girls High School Management System",
    version="0.1.0",
)

# CORS - allows the frontend (served separately) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------
app.include_router(auth_routes.router)
app.include_router(academic_routes.router)
app.include_router(teacher_routes.router)
app.include_router(student_routes.router)
app.include_router(attendance_routes.router)
app.include_router(homework_routes.router)
app.include_router(timetable_routes.router)
app.include_router(exam_routes.router)
app.include_router(result_routes.router)
app.include_router(fee_routes.router)
app.include_router(notice_routes.router)
app.include_router(notification_routes.router)
app.include_router(report_routes.router)
app.include_router(upload_routes.router)
app.include_router(backup_routes.router)

# Serve uploaded files (profile photos, homework attachments) back to the frontend
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Part 6+ will add:
# frontend templates (public site, dashboards) — no more backend routers planned


@app.on_event("startup")
async def capture_event_loop():
    """Lets synchronous controller code push WebSocket notifications in real time
    (see app/utils/ws_manager.py)."""
    import asyncio
    manager.set_main_loop(asyncio.get_event_loop())


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "message": f"{settings.APP_NAME} API is running",
    }


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
