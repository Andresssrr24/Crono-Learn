from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.pomodoro import Pomodoro
class PomodoroTimer:
    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id

    async def create_pomodoro(self, rest_time: int, task_name: str, timer: int=25, status: str="scheduled"):
        new_pomodoro = Pomodoro(
            timer=timer,
            user_id=self.user_id,
            start_time=datetime.now(),
            rest_time=rest_time,
            task_name=task_name,
            status=status
        )
        self.db_add(new_pomodoro)
        await self.db.commit()
        return new_pomodoro

    async def stop(self):  # db model ready to start implementation
        pass

    async def pause(): 
        pass

    async def resume():
        pass

    async def extend():
        pass

    async def complete():
        pass

    async def _get_pomodoro():
        pass

    async def _register_study_time():
        pass

