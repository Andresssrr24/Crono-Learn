from app.db.base import Base
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey

class Pomodoro(Base):
    __tablename__ = "pomodoros_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timer: Mapped[int] = mapped_column(Integer, nullable=False)
    rest_time: Mapped[int] = mapped_column(Integer, nullable=True)
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    task_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=True)  # possible values: "running", "stopped", "finished", "scheduled"
    user_id: Mapped[str] = mapped_column(ForeignKey("user.id"), nullable=False)


