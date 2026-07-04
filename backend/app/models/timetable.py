from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint, Time, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import datetime as dt
import enum

class WeekdayEnum(enum.IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

class TimetableSlot(Base):
    __tablename__ = "timetable_slot"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    semester_id: Mapped[int] = mapped_column(ForeignKey("semester_profile.id", ondelete="CASCADE"), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subject.id", ondelete="CASCADE"), nullable=False)
    weekday: Mapped[WeekdayEnum] = mapped_column(Enum(WeekdayEnum), nullable=False)
    start_time: Mapped[dt.time] = mapped_column(Time, nullable=False)
    end_time: Mapped[dt.time] = mapped_column(Time, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)

    semester = relationship("SemesterProfile", back_populates="timetable_slots")
    subject = relationship("Subject", back_populates="timetable_slots")

    __table_args__ = (
        CheckConstraint('start_time < end_time', name='check_time_range'),
    )
