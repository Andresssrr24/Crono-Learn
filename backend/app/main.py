from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.v1.endpoints import user, pomodoro 
from app.db.session import engine
from app.db.base import Base 

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="CronoLearn",
    version="0.1.0",
    description="CronoLearn API backend",
    lifespan=lifespan 
)

app.include_router(user.router, prefix="/api/v1/users")
app.include_router(pomodoro.router, prefix="/api/v1/pomodoro")

@app.get("/")
async def root():
    return {"message": "Welcome to CronoLearn"}