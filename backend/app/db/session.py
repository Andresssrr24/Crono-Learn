from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

DATABASE_URL = get_settings().DATABASE_URL

engine = create_async_engine(DATABASE_URL, future=True, echo=True)
AsyncSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=True, 
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
    )

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session