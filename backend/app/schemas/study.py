from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional

class StudyCreate(BaseModel):
    topic: str = Field(..., examples="Maths")
    study_time: int = Field(..., gt=0, examples=50)
    notes: Optional[str] = Field(None, examples="Solved some exercises")
    timestamp: Optional[datetime] = Field(datetime.now(timezone.utc))

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "topic": "History",
                    "study_time": 40,
                    "notes": "book summary",
                    "timestamp": "2025-07-17T12:00:00Z"
                }
            ]
        }
    }

class StudyResponse(BaseModel):
    id: int
    topic: Optional[str]
    study_time: int
    notes: Optional[str]
    timestamp: datetime
    user_id: str

    class Config:
        orm_mode = True