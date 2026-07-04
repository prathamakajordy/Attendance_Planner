from sqlalchemy import Column, Integer, String, Float, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Subject(Base):
    __tablename__ = "subject"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    semester_id: Mapped[int] = mapped_column(ForeignKey("semester_profile.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=True)
    min_percentage_override: Mapped[float] = mapped_column(Float, nullable=True)
    held_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    present_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    semester = relationship("SemesterProfile", back_populates="subjects")
    timetable_slots = relationship("TimetableSlot", back_populates="subject", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint('held_count >= 0', name='check_held_positive'),
        CheckConstraint('present_count >= 0', name='check_present_positive'),
        CheckConstraint('present_count <= held_count', name='check_present_lte_held'),
    )
