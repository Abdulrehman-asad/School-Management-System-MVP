"""
Routes for file uploads: profile photos (student/teacher/admin, own account
only) and homework attachments (teacher, own homework only).

Uploaded files are served back from the /uploads static mount registered in
main.py, so the returned path can be used directly as e.g.
f"{API_BASE}/uploads/{profile_image}" on the frontend.
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.homework import Homework
from app.utils.file_storage import save_profile_photo, save_homework_attachment, delete_uploaded_file
from app.controllers.teacher_controller import get_teacher_by_user_id

router = APIRouter(prefix="/api/uploads", tags=["Uploads"])


@router.post("/profile-photo")
def upload_profile_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Any authenticated user can upload/replace their own profile photo."""
    old_path = current_user.profile_image
    new_path = save_profile_photo(file)

    current_user.profile_image = new_path
    db.commit()

    delete_uploaded_file(old_path)  # clean up the old photo, best-effort

    return {"profile_image": new_path, "url": f"/uploads/{new_path}"}


@router.post("/homework/{homework_id}/attachment")
def upload_homework_attachment(
    homework_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """A teacher can attach a file to homework they assigned."""
    if current_user.role.role_name != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can upload homework attachments")

    teacher = get_teacher_by_user_id(db, current_user.user_id)
    homework = db.query(Homework).filter(Homework.homework_id == homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="Homework not found")
    if homework.teacher_id != teacher.teacher_id:
        raise HTTPException(status_code=403, detail="You can only attach files to your own homework")

    old_path = homework.attachment_path
    new_path = save_homework_attachment(file)

    homework.attachment_path = new_path
    db.commit()

    delete_uploaded_file(old_path)

    return {"attachment_path": new_path, "url": f"/uploads/{new_path}"}
