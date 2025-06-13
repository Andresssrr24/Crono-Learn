from app.db.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

async def get_user_by_id(db: AsyncSession, user_id: str):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def create_user_if_not_exists(db: AsyncSession, user_data: dict):
    user = await get_user_by_id(db, user_data["id"])
    if user:
        return user

    new_user = User(
        id=user_data["id"],
        email=user_data["email"],
        full_name=user_data.get("full_name"),
        created_at=user_data.get("created_at")
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user