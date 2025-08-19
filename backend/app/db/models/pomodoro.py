from app.db.base import Base
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey

class Pomodoro(Base):
    __tablename__ = "pomodoros_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timer: Mapped[int] = mapped_column(Integer, nullable=False)
    rest_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[datetime] = mapped_column(DateTime, default=None, nullable=True)
    last_resume_time: Mapped[datetime] = mapped_column(DateTime, default=None, nullable=True)
    worked_time: Mapped[int] = mapped_column(Integer, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=True)
    task_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="scheduled", nullable=True)  # possible values: "running", "stopped", "finished", "scheduled"
    user_id: Mapped[str] = mapped_column(nullable=False)


