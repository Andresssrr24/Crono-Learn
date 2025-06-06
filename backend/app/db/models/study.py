from app.db.base import Base
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Text

class Study(Base):
    __tablename__ = "study_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic: Mapped[Optional[str]] = mapped_column(String(75), nullable=True)
    study_time: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True) 
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.timezone())
