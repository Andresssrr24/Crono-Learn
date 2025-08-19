from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.pomodoro import Pomodoro
from sqlalchemy.future import select
from sqlalchemy import update
import asyncio
class PomodoroTimer:
    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id

    async def create_pomodoro(self, rest_time: int, task_name: str, timer: int=25, status: str="scheduled"):
        if timer <= 0:
            raise ValueError("Pomodoro timer has to be greater than 0.")
        if rest_time < 0:
            raise ValueError("Rest timer cannot be negative.")

        new_pomodoro = Pomodoro(
            timer=timer,
            start_time=datetime.now(),
            rest_time=rest_time,
            task_name=task_name,
            worked_time=0,  
            last_resume_time=None,
            user_id=self.user_id,
            status=status,
            end_time=None,
        )

        self.db.add(new_pomodoro)
        await self.db.flush()

        asyncio.create_task(self.run_pomodoro(new_pomodoro.id))

        await self.db.commit()
        return new_pomodoro
    
    async def run_pomodoro(self, pomodoro_id: str):
        try:
            result = await self.db.execute(
                select(Pomodoro).where(Pomodoro.id == pomodoro_id, Pomodoro.user_id == self.user_id)
            )
            pomodoro = result.scalar_one_or_none()
            if not pomodoro:
                return
            
            total_seconds = pomodoro.timer
            interval = 1 
            elapsed = 0

            while elapsed < total_seconds:
                await asyncio.sleep(interval)
                elapsed += interval
                
                await self.update_progress(pomodoro_id, elapsed)

            await self.completed(pomodoro_id)

            print(f"Pomodoro {pomodoro.id} finished!.")

        except Exception as e:
            await self.failed(pomodoro_id)

    async def update_progress(self, pomodoro_id: str, elapsed: int):
        '''Update pomodoro progress'''
        await self.db.execute(
            update(Pomodoro).where(Pomodoro.id == pomodoro_id).values(worked_time=elapsed)
        )

        await self.db.commit()

    async def completed(self, pomodoro_id: str):
        '''When a pomodoro is successfully finished'''
        await self.db.execute(
            update(Pomodoro).where(Pomodoro.id == pomodoro_id).values(status='completed', end_time=datetime.now())
        )

        await self.db.commit()

    async def failed(self, pomodoro_id: str):
        '''When a pomodoro execution fails'''
        await self.db.execute(
            update(Pomodoro).where(Pomodoro.id == pomodoro_id).values(status='failed')
        )

        await self.db.commit()

    async def stop(self, pomodoro_id: str, user_id: str):
        pomodoro = await self._get_pomodoro(pomodoro_id, user_id)

        if not pomodoro:
            return None
        if pomodoro.completed == True:
            raise ValueError('Cannot play with a finished pomodoro.')
        if pomodoro.status == "stopped":
            raise ValueError('Pomodoro is already stopped.')
        
        if pomodoro.status == "running" and pomodoro.last_resume_time:
            now = datetime.now()
            elapsed = (now - pomodoro.last_resume_time).total_seconds()
            pomodoro.worked_time += int(elapsed)

        pomodoro.status = "stopped"
        pomodoro.last_resume_time = None

        self.db.add(pomodoro)
        await self.db.commit()
        return pomodoro

    async def pause(self, pomodoro_id: str, user_id: str):
        pomodoro = await self._get_pomodoro(pomodoro_id, user_id)

        if not pomodoro:
            return None
        if pomodoro.completed == True:
            raise ValueError('Cannot play with a finished pomodoro.')
        if pomodoro.status != "running":
            raise ValueError("Cannot pause a pomodoro that is not running.")
        
        if pomodoro.last_resume_time:
            now = datetime.now()
            elapsed = (now - pomodoro.last_resume_time).total_seconds()
            pomodoro.worked_time += int(elapsed)

        pomodoro.status = "paused"
        pomodoro.last_resume_time = None

        self.db.add(pomodoro)
        await self.db.commit()
        return pomodoro

    async def resume(self, pomodoro_id: str, user_id: str):
        pomodoro = await self._get_pomodoro(pomodoro_id, user_id)

        if not pomodoro:
            return None
        if pomodoro.completed == True:
            raise ValueError('Cannot play with a finished pomodoro.')
        if pomodoro.status == "running":
            raise ValueError('Pomodoro is already running.')
        if pomodoro.status == "stopped":
            raise ValueError('Cannot resume a pomodoro that was stopped.')

        pomodoro.status = "running"
        pomodoro.last_resume_time = datetime.now()

        self.db.add(pomodoro)
        await self.db.commit()
        return pomodoro    

    async def extend(self, pomodoro_id: str, add_time: int):
        pomodoro = await self._get_pomodoro(pomodoro_id)

        if not pomodoro:
            return None
        if pomodoro.completed == True:
            raise ValueError('Cannot play with a finished pomodoro.')
        if pomodoro.status == "stopped":
            raise ValueError('Cannot extend a pomodoro that was stopped.')
        
        pomodoro.timer += add_time.total_seconds()
        self.db.add(pomodoro)
        await self.db.commit()
        return pomodoro

    async def _get_pomodoro(self, pomodoro_id: str, user_id: str):
        result = await self.db.execute(select(Pomodoro).where(Pomodoro.id == int(pomodoro_id), Pomodoro.user_id == user_id)) 
        return result.scalar_one_or_none()