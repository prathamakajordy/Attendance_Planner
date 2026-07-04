from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class EventTypeDefinition(Base):
    __tablename__ = "event_type_definition"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String, nullable=False)
    is_system_preset: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    default_cancels_lectures: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    default_counts_towards_attendance: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    default_is_working_day: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    default_exclude_from_recommendation: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
