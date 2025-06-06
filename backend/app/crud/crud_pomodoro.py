from app.db.models.pomodoro import Pomodoro
from app.schemas.pomodoro import PomodoroCreate
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

async def create_pomodoro(db: AsyncSession, pomodoro: PomodoroCreate):
    new_pomodoro = Pomodoro(
        timer=pomodoro.timer,
        rest_time=pomodoro.rest_time,
        start_time=datetime.now(timezone.utc)
    )
    db.add(new_pomodoro)
    await db.commit()
    await db.refresh(new_pomodoro)

    return new_pomodoro

async def get_pomodoros(db: AsyncSession):
    result = await db.execute(select(Pomodoro))
    return result.scalars().all()

async def get_pomodoro_by_id(db: AsyncSession, pomodoro_id: int):
    result = await db.execute(select(Pomodoro).where(Pomodoro.id == pomodoro_id))
    return result.scalar_one_or_none()

async def delete_pomodoro(db: AsyncSession, pomodoro_id: int):
    pomodoro = await get_pomodoro_by_id(db, pomodoro_id)
    if pomodoro:
        await db.delete(pomodoro)
        await db.commit()
    return pomodoro
