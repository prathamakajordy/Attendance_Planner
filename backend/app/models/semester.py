from sqlalchemy import Column, Integer, String, Date, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import datetime as dt
from sqlalchemy.dialects.sqlite import JSON
from app.db.base import Base

class SemesterProfile(Base):
    __tablename__ = "semester_profile"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[dt.date] = mapped_column(Date, nullable=False)
    end_date: Mapped[dt.date] = mapped_column(Date, nullable=False)
    min_overall_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    min_subject_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    student_groups: Mapped[list[str]] = mapped_column(JSON, default=list, server_default='[]')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subjects = relationship("Subject", back_populates="semester", cascade="all, delete-orphan")
    timetable_slots = relationship("TimetableSlot", back_populates="semester", cascade="all, delete-orphan")
    events = relationship("SemesterEvent", back_populates="semester", cascade="all, delete-orphan")
    plan_metadata = relationship("PlanMetadata", back_populates="semester", uselist=False, cascade="all, delete-orphan")
    plan_days = relationship("PlanDay", back_populates="semester", cascade="all, delete-orphan")
