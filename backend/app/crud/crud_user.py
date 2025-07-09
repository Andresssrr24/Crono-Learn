from app.db.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def create_user_if_not_exists(db: AsyncSession, email:str):
    user = await get_user_by_email(db, email)
    if user:
        return user

    new_user = User(email=email)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user