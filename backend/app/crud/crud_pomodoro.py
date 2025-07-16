from app.db.models.pomodoro import Pomodoro
from app.schemas.pomodoro import PomodoroCreate
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

async def create_pomodoro(db: AsyncSession, pomodoro: PomodoroCreate, user_id: str):
    new_pomodoro = Pomodoro(
        user_id = user_id,
        timer=pomodoro.timer,
        rest_time=pomodoro.rest_time,
        start_time=datetime.now(timezone.utc),
        task_name=pomodoro.task_name,
        status=pomodoro.status,
        last_resume_time=None,
        worked_time=pomodoro.worked_time
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

async def update_pomodoro(db: AsyncSession, pomodoro_id: int, pomodoro_data: dict):
    pomodoro = await get_pomodoro_by_id(db, pomodoro_id)
    if not pomodoro:
        return None
    for k, v in pomodoro.items():
        setattr(pomodoro, k, v)
    await db.commit()
    await db.refresh(pomodoro)
    return pomodoro
        
