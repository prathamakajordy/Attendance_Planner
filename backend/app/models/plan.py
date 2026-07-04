from sqlalchemy import Integer, String, Date, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import datetime as dt
from app.db.base import Base


class PlanMetadata(Base):
    """Stores metadata for the currently active recommendation plan for a semester.
    
    One-to-one relationship with SemesterProfile. When a new plan is generated,
    the old metadata row is replaced (upserted).
    """
    __tablename__ = "plan_metadata"
    semester_id: Mapped[int] = mapped_column(
        ForeignKey("semester_profile.id", ondelete="CASCADE"),
        primary_key=True
    )
    generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    engine_version: Mapped[str] = mapped_column(String, nullable=False)
    overall_feasible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    overall_attendance_threshold: Mapped[float] = mapped_column(nullable=False)
    subject_attendance_threshold: Mapped[float] = mapped_column(nullable=False)

    semester = relationship("SemesterProfile", back_populates="plan_metadata")


class PlanDay(Base):
    """Stores a single calendar day within the generated recommendation plan.
    
    Each day records whether it is a lecture day and optionally carries
    a day-level explanation (e.g. "No lectures due to Holiday").
    """
    __tablename__ = "plan_day"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    semester_id: Mapped[int] = mapped_column(
        ForeignKey("semester_profile.id", ondelete="CASCADE"),
        nullable=False
    )
    date: Mapped[dt.date] = mapped_column(Date, nullable=False)
    is_lecture_day: Mapped[bool] = mapped_column(Boolean, nullable=False)
    day_explanation: Mapped[str | None] = mapped_column(String, nullable=True)

    semester = relationship("SemesterProfile", back_populates="plan_days")
    blocks = relationship("PlanBlock", back_populates="plan_day", cascade="all, delete-orphan")


class PlanBlock(Base):
    """Stores a continuous time block within a PlanDay.
    
    Each block contains one or more subject IDs (stored as JSON string),
    a recommendation ("Attend", "Skip", or "Optional"), and an explanation.
    """
    __tablename__ = "plan_block"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plan_day_id: Mapped[int] = mapped_column(
        ForeignKey("plan_day.id", ondelete="CASCADE"),
        nullable=False
    )
    start_time: Mapped[dt.time] = mapped_column(nullable=False)
    end_time: Mapped[dt.time] = mapped_column(nullable=False)
    subject_ids: Mapped[str] = mapped_column(String, nullable=False)  # JSON-encoded list[int]
    recommendation: Mapped[str] = mapped_column(String, nullable=False)  # "Attend" | "Skip" | "Optional"
    block_explanation: Mapped[str | None] = mapped_column(String, nullable=True)

    plan_day = relationship("PlanDay", back_populates="blocks")

    @property
    def subject_ids_list(self) -> list[int]:
        """Deserializes the JSON-encoded subject_ids column."""
        import json
        return json.loads(self.subject_ids)

    @subject_ids_list.setter
    def subject_ids_list(self, value: list[int]):
        """Serializes a list of ints into the JSON subject_ids column."""
        import json
        self.subject_ids = json.dumps(value)
