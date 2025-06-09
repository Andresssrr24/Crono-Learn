from .models import *
from .session import engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)