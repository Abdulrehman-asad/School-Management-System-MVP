"""
Shared file-upload validation and storage helpers.

Files are saved under backend/uploads/<category>/<uuid>.<ext> and served back
via the /uploads static mount registered in main.py. Filenames are never
trusted from the client — we generate our own to avoid path traversal and
collisions.
"""

import uuid
from pathlib import Path
from typing import Set

from fastapi import UploadFile, HTTPException

from app.config import settings

UPLOAD_ROOT = Path(settings.UPLOAD_DIR)

IMAGE_EXTENSIONS: Set[str] = {".jpg", ".jpeg", ".png", ".webp"}
HOMEWORK_EXTENSIONS: Set[str] = {".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png"}


def _validate_and_save(
    file: UploadFile,
    subfolder: str,
    allowed_extensions: Set[str],
    max_mb: int,
) -> str:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Allowed types: {', '.join(sorted(allowed_extensions))}",
        )

    contents = file.file.read()
    max_bytes = max_mb * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File exceeds the {max_mb}MB size limit")
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    target_dir = UPLOAD_ROOT / subfolder
    target_dir.mkdir(parents=True, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex}{ext}"
    target_path = target_dir / unique_name
    with open(target_path, "wb") as out:
        out.write(contents)

    # Path returned is relative to the /uploads static mount, e.g. "profile_pictures/abc123.jpg"
    return f"{subfolder}/{unique_name}"


def save_profile_photo(file: UploadFile) -> str:
    return _validate_and_save(file, "profile_pictures", IMAGE_EXTENSIONS, settings.MAX_PROFILE_PHOTO_MB)


def save_homework_attachment(file: UploadFile) -> str:
    return _validate_and_save(file, "homework", HOMEWORK_EXTENSIONS, settings.MAX_HOMEWORK_ATTACHMENT_MB)


def delete_uploaded_file(relative_path: str) -> None:
    """Best-effort delete — used when replacing a profile photo. Never raises."""
    if not relative_path:
        return
    try:
        full_path = UPLOAD_ROOT / relative_path
        if full_path.resolve().is_relative_to(UPLOAD_ROOT.resolve()) and full_path.exists():
            full_path.unlink()
    except Exception:
        pass
