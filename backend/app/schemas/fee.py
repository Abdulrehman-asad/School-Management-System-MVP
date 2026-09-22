"""
Pydantic request/response models for the Fee Management module.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from decimal import Decimal

from app.models.fee import FeeFrequency, ChallanStatus


# ---------------------------------------------------------------------
# Fee Structure
# ---------------------------------------------------------------------
class FeeStructureCreate(BaseModel):
    class_id: int
    fee_title: str = Field(..., max_length=100, examples=["Tuition Fee"])
    amount: Decimal = Field(..., gt=0)
    frequency: FeeFrequency = FeeFrequency.monthly


class FeeStructureUpdate(BaseModel):
    fee_title: Optional[str] = Field(None, max_length=100)
    amount: Optional[Decimal] = Field(None, gt=0)
    frequency: Optional[FeeFrequency] = None


class FeeStructureOut(BaseModel):
    fee_structure_id: int
    class_id: int
    fee_title: str
    amount: Decimal
    frequency: FeeFrequency

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------
# Fee Challan
# ---------------------------------------------------------------------
class ChallanGenerateForStudent(BaseModel):
    """Generate one challan for one student against a fee structure."""
    student_id: int
    fee_structure_id: int
    month_year: Optional[str] = Field(None, examples=["August 2026"])
    due_date: date
    fine_amount: Decimal = Decimal("0")


class ChallanGenerateForClass(BaseModel):
    """Generate challans for every active student in a class/section at once."""
    fee_structure_id: int
    section_id: int
    month_year: Optional[str] = Field(None, examples=["August 2026"])
    due_date: date


class ChallanPayRequest(BaseModel):
    payment_method: str = Field(..., examples=["cash", "bank_transfer", "online"])
    paid_date: Optional[date] = None


class FeeChallanUpdate(BaseModel):
    due_date: Optional[date] = None
    fine_amount: Optional[Decimal] = None
    status: Optional[ChallanStatus] = None


class FeeChallanOut(BaseModel):
    challan_id: int
    student_id: int
    fee_structure_id: int
    challan_no: str
    month_year: Optional[str] = None
    amount: Decimal
    fine_amount: Decimal
    due_date: date
    paid_date: Optional[date] = None
    status: ChallanStatus
    payment_method: Optional[str] = None

    class Config:
        from_attributes = True


class FeeCollectionSummary(BaseModel):
    """Powers the admin dashboard's fee collection chart/card."""
    total_challans: int
    total_amount_billed: Decimal
    total_amount_collected: Decimal
    total_amount_pending: Decimal
    paid_count: int
    unpaid_count: int
    overdue_count: int
