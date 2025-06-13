from pydantic import BaseModel
from typing import Optional

class UserOut(BaseModel):
    id: str
    emai: str
    username: Optional[str]

    class config:
        orm_mode = True