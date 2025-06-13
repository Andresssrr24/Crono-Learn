from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.pomodoro import Pomodoro
class PomodoroTimer:
    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id

    async def create_pomodoro(self, rest_time: int, task_name: str, timer: int=25):
        new_pomodoro = Pomodoro(
            timer=timer,
            user_id=self.user_id,
            start_time=datetime.now(),
            rest_time=rest_time,
            task_name=task_name
        )

    async def stop(self, ):  # ! Before implement this, add status field (running/stopped/finished)
        pass

    async def pause():  # ! Watch on deepseek
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

