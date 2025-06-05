from app.db.base import base
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column

class Pomodoro(base):
    __tablename__ = "pomodoros_history"

    id: Mapped[int] = mapped_column()
    timer: int = int
    rest_time: int = int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    completed: Optional[bool] = True
    task_name: Optional[str] = None 

