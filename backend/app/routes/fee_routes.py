"""
Routes for Fee Structures and Fee Challans.

Fee structure & challan generation/edit/delete: admin, super_admin only.
Reading challans: admin/super_admin see everyone; a student sees only their own
(needed for the Student Dashboard's fee status widget).
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models.user import User
from app.controllers import fee_controller as crud
from app.controllers.student_controller import get_student_by_user_id
from app.schemas.fee import (
    FeeStructureCreate, FeeStructureUpdate, FeeStructureOut,
    ChallanGenerateForStudent, ChallanGenerateForClass, ChallanPayRequest, FeeChallanUpdate,
    FeeChallanOut, FeeCollectionSummary,
)

router = APIRouter(prefix="/api/fees", tags=["Fee Management"])

ADMIN_ONLY = require_roles("admin", "super_admin")


# ---------------------------------------------------------------------
# Fee Structures
# ---------------------------------------------------------------------
@router.post("/structures", response_model=FeeStructureOut, status_code=201)
def create_fee_structure(payload: FeeStructureCreate, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    return crud.create_fee_structure(db, payload)


@router.get("/structures", response_model=List[FeeStructureOut])
def list_fee_structures(
    class_id: Optional[int] = Query(None),
    db: Session = Depends(get_db), _=Depends(get_current_user),
):
    return crud.list_fee_structures(db, class_id)


@router.get("/structures/{fee_structure_id}", response_model=FeeStructureOut)
def get_fee_structure(fee_structure_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return crud.get_fee_structure(db, fee_structure_id)


@router.put("/structures/{fee_structure_id}", response_model=FeeStructureOut)
def update_fee_structure(
    fee_structure_id: int, payload: FeeStructureUpdate,
    db: Session = Depends(get_db), _=Depends(ADMIN_ONLY),
):
    return crud.update_fee_structure(db, fee_structure_id, payload)


@router.delete("/structures/{fee_structure_id}", status_code=204)
def delete_fee_structure(fee_structure_id: int, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    crud.delete_fee_structure(db, fee_structure_id)


# ---------------------------------------------------------------------
# Fee Challans
# ---------------------------------------------------------------------
@router.post("/challans/generate/student", response_model=FeeChallanOut, status_code=201)
def generate_challan_for_student(
    payload: ChallanGenerateForStudent, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY),
):
    return crud.generate_challan_for_student(db, payload)


@router.post("/challans/generate/class", response_model=List[FeeChallanOut], status_code=201)
def generate_challans_for_class(
    payload: ChallanGenerateForClass, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY),
):
    """Bulk-generates a challan for every active student in a section — e.g. monthly tuition fee."""
    return crud.generate_challans_for_class(db, payload)


@router.get("/challans", response_model=List[FeeChallanOut])
def list_challans(
    student_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    month_year: Optional[str] = Query(None),
    skip: int = 0, limit: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = current_user.role.role_name
    if role == "student":
        student = get_student_by_user_id(db, current_user.user_id)
        student_id = student.student_id  # force students to only see their own challans
    elif role not in ("admin", "super_admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    return crud.list_challans(db, student_id, status_filter, month_year, skip, limit)


@router.get("/challans/summary", response_model=FeeCollectionSummary)
def get_collection_summary(
    month_year: Optional[str] = Query(None),
    db: Session = Depends(get_db), _=Depends(ADMIN_ONLY),
):
    """Powers the admin dashboard's fee-collection chart/card."""
    return crud.get_collection_summary(db, month_year)


@router.get("/challans/{challan_id}", response_model=FeeChallanOut)
def get_challan(
    challan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = current_user.role.role_name
    challan = crud.get_challan(db, challan_id)

    if role == "student":
        student = get_student_by_user_id(db, current_user.user_id)
        if challan.student_id != student.student_id:
            raise HTTPException(status_code=403, detail="You can only view your own fee challans")
    elif role not in ("admin", "super_admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    return challan


@router.put("/challans/{challan_id}/pay", response_model=FeeChallanOut)
def pay_challan(
    challan_id: int, payload: ChallanPayRequest,
    db: Session = Depends(get_db), _=Depends(ADMIN_ONLY),
):
    """Marks a challan as paid — records payment method and date, prints a receipt-ready record."""
    return crud.pay_challan(db, challan_id, payload)


@router.put("/challans/{challan_id}", response_model=FeeChallanOut)
def update_challan(
    challan_id: int, payload: FeeChallanUpdate,
    db: Session = Depends(get_db), _=Depends(ADMIN_ONLY),
):
    return crud.update_challan(db, challan_id, payload)


@router.delete("/challans/{challan_id}", status_code=204)
def delete_challan(challan_id: int, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    crud.delete_challan(db, challan_id)
