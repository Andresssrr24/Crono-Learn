from fastapi import FastAPI
from .api.v1.endpoints import pomodoro, stats, study, user
from .core.config import get_settings
from .db.base import Base
from .db.session import engine

app = FastAPI(
    title="CronoLearn",
    version="0.1.0",
    description="CronoLearn API backend"
)

settings = get_settings(0)

Base.metadata.create_all(engine)

app.include_router(user.router, prefix='/api/v1/users', tags=['Users'])

@app.get("/")
def read_root():
    return {"test" : "one"}
