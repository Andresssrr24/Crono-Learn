from app.db.models.user import User
from app.schemas.user import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

async def create_user(db: AsyncSession, user: UserCreate):
    new_user = User (
        email=user.email,
        password=user.password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

async def get_users(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    result = result.scalar_one_or_none()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return result

async def delete_user(db: AsyncSession, email: int):
    user = await get_user_by_email(db, email)
    if user:
        await db.delete(user)
        await db.commit()
    return user

async def update_user(db: AsyncSession, email: str, user_data: dict):
    user = await get_user_by_email(db. email)
    if not user:
        return None
    for k, v in user_data.items():
        setattr(user, k, v)
    await db.commit()
    await db.refresh(user)
    return user
