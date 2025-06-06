from app.db.models.user import User
from app.schemas.user import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

async def create_user(db: AsyncSession, user: UserCreate):
    new_user = User (
        email=user.email,
        password=user.password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

async def get_pomodoros(db: AsyncSession):
    pass