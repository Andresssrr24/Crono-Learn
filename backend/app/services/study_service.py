from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.study import Study
from sqlalchemy.future import select

class StudyService:
    def __init__(self, db: AsyncSession, user_email: str):
        self.db = db
        self.user_id = user_email

    async def create_study_record(self, topic: str, study_time: int, notes: str = None):
        if study_time <= 0:
            raise ValueError("Study time must be greater than 0.")

        new_study_record = Study(
            user_id=self.user_id,
            topic=topic,
            study_time=study_time,
            notes=notes
        )
        self.db.add(new_study_record)
        await self.db.commit()
        await self.db.refresh(new_study_record)
        return new_study_record

    async def get_study_records(self):
        query = select(Study).where(Study.user_id == self.user_id)
        result = await self.db.execute(query)
        return result.scalars().all() 
    
    async def delete_study_record(self, record_id: int):
        query = select(Study).where(Study.id == record_id, Study.user_id == self.user_id)
        result = await self.db.execute(query)
        study_record = result.scalar_one_or_none()

        if not study_record:
            raise ValueError("Study record not found or user is not authorized.")

        await self.db.delete(study_record)
        await self.db.commit()
        return study_record