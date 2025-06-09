from fastapi import FastAPI
from .api.v1.endpoints import pomodoro, stats, study, user
from .core.config import get_settings
from .db.base import init_models
from .db.session import engine

settings = get_settings()

async def lifespan(app: FastAPI):
    await init_models()
    yield

app = FastAPI(
    title="CronoLearn",
    version="0.1.0",
    description="CronoLearn API backend"
)

app.include_router(user.router, prefix='/api/v1/users', tags=['Users'])

@app.get("/")
def read_root():
    return {"message" : "Welcome to CronoLearn"}
