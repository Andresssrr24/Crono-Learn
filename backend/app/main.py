from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.v1.endpoints import user, pomodoro, study, agent
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router, prefix="/users")
app.include_router(pomodoro.router, prefix="/pomodoro")
app.include_router(study.router, prefix="/my-studies")
app.include_router(agent.router, prefix="/agent")

@app.get("/")
async def root():
    return {"message": "Welcome to CronoLearn"}