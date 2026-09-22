"""
Fee module models: the recurring fee structure defined per class (e.g. "Tuition
Fee: 5000/month for Class 9"), and the actual challans generated for students.
"""

from sqlalchemy import (
    Column, Integer, BigInteger, String, Date, DateTime, Numeric, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database.session import Base


class FeeFrequency(str, enum.Enum):
    monthly = "monthly"
    quarterly = "quarterly"
    annual = "annual"
    one_time = "one_time"


class FeeStructure(Base):
    __tablename__ = "fee_structures"

    fee_structure_id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.class_id", ondelete="CASCADE"), nullable=False)
    fee_title = Column(String(100), nullable=False)     # e.g. "Tuition Fee", "Admission Fee"
    amount = Column(Numeric(10, 2), nullable=False)
    frequency = Column(Enum(FeeFrequency), default=FeeFrequency.monthly)
    created_at = Column(DateTime, server_default=func.now())

    school_class = relationship("SchoolClass")
    challans = relationship("FeeChallan", back_populates="fee_structure")


class ChallanStatus(str, enum.Enum):
    unpaid = "unpaid"
    paid = "paid"
    overdue = "overdue"
    cancelled = "cancelled"


class FeeChallan(Base):
    __tablename__ = "fee_challans"

    challan_id = Column(BigInteger, primary_key=True, index=True)
    student_id = Column(BigInteger, ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    fee_structure_id = Column(Integer, ForeignKey("fee_structures.fee_structure_id"), nullable=False)
    challan_no = Column(String(40), unique=True, nullable=False)
    month_year = Column(String(20))                     # e.g. "August 2026"
    amount = Column(Numeric(10, 2), nullable=False)
    fine_amount = Column(Numeric(10, 2), default=0)
    due_date = Column(Date, nullable=False)
    paid_date = Column(Date, nullable=True)
    status = Column(Enum(ChallanStatus), default=ChallanStatus.unpaid)
    payment_method = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())

    student = relationship("Student")
    fee_structure = relationship("FeeStructure", back_populates="challans")
