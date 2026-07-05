import uuid
import datetime as dt
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base

class ImportTypeEnum(enum.Enum):
    timetable = "timetable"
    calendar = "calendar"

class ImportStatusEnum(enum.Enum):
    pending_review = "pending_review"
    confirmed = "confirmed"
    discarded = "discarded"

class ImportSession(Base):
    __tablename__ = "import_session"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    semester_id: Mapped[int] = mapped_column(ForeignKey("semester_profile.id", ondelete="CASCADE"), nullable=True)
    import_type: Mapped[ImportTypeEnum] = mapped_column(Enum(ImportTypeEnum), nullable=False)
    status: Mapped[ImportStatusEnum] = mapped_column(Enum(ImportStatusEnum), nullable=False, default=ImportStatusEnum.pending_review)
    extracted_payload: Mapped[list[dict]] = mapped_column(JSON, default=list, server_default='[]')
    file_path: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)

    semester = relationship("SemesterProfile")
