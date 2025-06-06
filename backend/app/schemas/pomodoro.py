from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional

class PomodoroCreate(BaseModel):
    task_name: Optional[str] = Field(..., examples="CronoLearn project")
    timer: int = Field(..., examples=60)
    rest_time: Optional[int] = Field(..., examples=10)

    class Config:
        schema_extra = {
            "example" : {
                "task_name" : "math lesson",
                "timer" : 120,
                "rest_time" : 20
            }
        }

class PomodoroUpdate(BaseModel):
    task_name: Optional[bool]
    completed: Optional[bool]
    end_time: Optional[datetime]

class PomodoroResponse(BaseModel):
    id: int
    timer: int
    rest_time: int
    start_time: Optional[datetime] = datetime.now(timezone.utc)
    end_time: Optional[datetime] = datetime.now(timezone.utc)
    completed: Optional[bool] = False
    task_name: Optional[str] = None

    class Config:
        orm_mode = True