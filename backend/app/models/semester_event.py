from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, CheckConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import datetime as dt
from app.db.base import Base

class SemesterEvent(Base):
    __tablename__ = "semester_event"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    semester_id: Mapped[int] = mapped_column(ForeignKey("semester_profile.id", ondelete="CASCADE"), nullable=False)
    event_type_id: Mapped[int] = mapped_column(ForeignKey("event_type_definition.id"), nullable=False)
    custom_type_label: Mapped[str] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[dt.date] = mapped_column(Date, nullable=False)
    end_date: Mapped[dt.date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    cancels_lectures_override: Mapped[bool] = mapped_column(Boolean, nullable=True)
    counts_towards_attendance_override: Mapped[bool] = mapped_column(Boolean, nullable=True)
    is_working_day_override: Mapped[bool] = mapped_column(Boolean, nullable=True)
    exclude_from_recommendation_override: Mapped[bool] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    event_type = relationship("EventTypeDefinition")
    semester = relationship("SemesterProfile", back_populates="events")

    @property
    def resolved_cancels_lectures(self) -> bool:
        return self.cancels_lectures_override if self.cancels_lectures_override is not None else self.event_type.default_cancels_lectures
        
    @property
    def resolved_counts_towards_attendance(self) -> bool:
        return self.counts_towards_attendance_override if self.counts_towards_attendance_override is not None else self.event_type.default_counts_towards_attendance
        
    @property
    def resolved_is_working_day(self) -> bool:
        return self.is_working_day_override if self.is_working_day_override is not None else self.event_type.default_is_working_day
        
    @property
    def resolved_exclude_from_recommendation(self) -> bool:
        return self.exclude_from_recommendation_override if self.exclude_from_recommendation_override is not None else self.event_type.default_exclude_from_recommendation

    __table_args__ = (
        CheckConstraint('end_date >= start_date', name='check_event_dates'),
    )
