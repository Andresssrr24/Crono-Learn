from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional

class PomodoroCreate(BaseModel):
    timer: int = Field(default=60, examples=60)
    rest_time: Optional[int] = Field(..., examples=10)
    start_time: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), examples="2025-07-17T12:00:00Z")
    end_time: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), examples="2025-07-17T12:30:00Z")
    last_resume_time: Optional[datetime] = None
    worked_time: Optional[int] = Field(default=0, examples=30)
    completed: Optional[bool] = Field(default=False, examples=False)
    task_name: Optional[str] = Field(..., examples="CronoLearn project")
    status: str = Field(default="scheduled")

    model_config = {
        "json_schema_extra": {
            "examples" : [
                {
                    "timer" : 60,
                    "rest_time" : 10,
                    "start_time" : "2025-07-17T12:00:00Z",
                    "end_time" : "2025-07-17T12:30:00Z",
                    "last_resume_time" : "2025-07-17T12:00:00Z",
                    "worked_time" : 30,
                    "completed" : False,
                    "task_name" : "math lesson",
                    "status" : "scheduled"
                }
            ]
        }
    }

class PomodoroUpdate(BaseModel):
    timer: Optional[int] = Field(None, ge=1)
    rest_time: Optional[int] = Field(None, ge=0)
    worked_time: Optional[int] = Field(None, ge=0)
    task_name: Optional[str] = Field(None)
    completed: Optional[bool] = Field(False)
    end_time: Optional[datetime]
    last_resume_time: Optional[datetime] 
    status: Optional[str]

class PomodoroResponse(BaseModel):
    id: int
    timer: int
    rest_time: int
    start_time: Optional[datetime] = datetime.now(timezone.utc)
    end_time: Optional[datetime] = datetime.now(timezone.utc)
    completed: Optional[bool] = False
    task_name: Optional[str] = None
    status: str = "scheduled"
    user_id: str

    class Config:
        orm_mode = True