from app.db.models.study import Study
from app.schemas.study import StudyCreate
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

async def create_study_session(db: AsyncSession, study: StudyCreate):
    new_study_session = Study(
        topic=study.topic,
        study_time=study.study_time,
        notes=study.notes,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(new_study_session)
    await db.commit()
    await db.refresh(new_study_session)

    return new_study_session

async def get_study_sessions(db: AsyncSession):
    result = await db.execute(select(Study))
    return result.scalars().all()

async def get_study_session_by_id(db: AsyncSession, study_session_id: int):
    result = await db.execute(select(Study).where(Study.id == study_session_id))
    return result.scalar_one_or_none()

async def delete_study_session(db: AsyncSession, study_session_id: int):
    study_session = await get_study_session_by_id(db, study_session_id)
    if study_session:
        await db.delete(study_session)
        await db.commit()
    return study_session        