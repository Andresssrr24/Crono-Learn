from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class StudyCreate(BaseModel):
    topic: str = Field(..., examples="Maths")
    study_time: int = Field(..., gt=0, examples=50)
    notes: Optional[str] = Field(None, examples="Solved some exercises")

    class Config:
        schema_extra = {
            "example" : {
                "topic" : "History",
                "study_time" : 40,
                "notes" : "book summary"
            }
        }

class StudyResponse(BaseModel):
    id: int
    topic: str
    study_time: int
    notes: Optional[str]
    timestamp: datetime

    class Config:
        orm_mode = True