from datetime import datetime, timedelta
from app.db.models.pomodoro import Pomodoro
from app.db.session import AsyncSessionLocal
from sqlalchemy.future import select
from sqlalchemy import update
import asyncio

class PomodoroTimer:
    _instances = {}
    running_tasks: dict[str, dict[int, asyncio.Task]] = {}

    def __new__(cls, user_id: str):
        if user_id not in cls._instances:
            instance = super(PomodoroTimer, cls).__new__(cls)
            cls._instances[user_id] = instance
            cls.running_tasks[user_id] = {}
        return cls._instances[user_id]

    def __init__(self, user_id: str):
        if not hasattr(self, 'user_id'):
            self.user_id = user_id

    async def create_pomodoro(self, rest_time: int, task_name: str, timer: int=25, status: str="scheduled"):
        if timer <= 0:
            raise ValueError("Pomodoro timer has to be greater than 0.")
        if rest_time < 0:
            raise ValueError("Rest timer cannot be negative.")

        async with AsyncSessionLocal() as db:
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

            db.add(new_pomodoro)
            await db.commit()
            await db.refresh(new_pomodoro)  # Refresh to get ID
            
        task = asyncio.create_task(self.run_pomodoro(new_pomodoro.id))
        print(f'TASK created {task}')
        self.running_tasks[self.user_id][new_pomodoro.id] = task
        
        return new_pomodoro
    
    async def run_pomodoro(self, pomodoro_id: str, status: str="running"):
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Pomodoro).
                    where(Pomodoro.id == pomodoro_id, Pomodoro.user_id == self.user_id),
                )

                pomodoro = result.scalar_one_or_none()
                 
                if not pomodoro:
                    return
                
                #pomodoro.status = status
                total_seconds = pomodoro.timer
                interval = 1 
                elapsed = pomodoro.worked_time

                print(f"CURRENT TASK: {asyncio.current_task()}")
                while elapsed < total_seconds:
                    try:
                        await asyncio.wait_for(asyncio.sleep(interval), timeout=interval)
                    except asyncio.TimeoutError:
                        pass # Sleep finished normally
                    except asyncio.CancelledError:
                        print(f"Pomodoro {pomodoro_id} cancelled during sleep")
                        raise
                    
                    if asyncio.current_task().cancelled():
                        print(f"Pomodoro {pomodoro_id} cancellation detected")
                        raise asyncio.CancelledError()
                    
                    elapsed += interval

                    if elapsed % 5 == 0: # Update every 5 sec
                        await self.update_progress(pomodoro_id, elapsed, status)

                await self.completed(pomodoro_id)
                print(f"Pomodoro {pomodoro.id} finished!.")

        except asyncio.CancelledError:
            print(f"Pomodoro {pomodoro_id} was cancelled.")
        except Exception as e:
            print(f"Pomodoro {pomodoro_id} failed: {e}")
            await self.failed(pomodoro_id)

    async def update_progress(self, pomodoro_id: str, elapsed: int, status: str):
        '''Update pomodoro progress'''
        async with AsyncSessionLocal() as db:
            await db.execute(
                update(Pomodoro)
                .where(Pomodoro.id == pomodoro_id, Pomodoro.user_id == self.user_id)
                .values(worked_time=elapsed, status=status)
            )

            await db.commit()

    async def completed(self, pomodoro_id: str):
        '''When a pomodoro is successfully finished'''
        async with AsyncSessionLocal() as db:
            await db.execute(
                update(Pomodoro)
                .where(Pomodoro.id == pomodoro_id, Pomodoro.user_id == self.user_id)
                .values(status='completed', end_time=datetime.now())
            )

            await db.commit()

        # clean up task
        if self.user_id in self.running_tasks and pomodoro_id in self.running_tasks[self.user_id]:
            del self.running_tasks[self.user_id][pomodoro_id]

    async def failed(self, pomodoro_id: str):
        '''When a pomodoro execution fails'''
        async with AsyncSessionLocal() as db:
            await db.execute(
                update(Pomodoro)
                .where(Pomodoro.id == pomodoro_id, Pomodoro.user_id == self.user_id)
                .values(status='failed')
            )

            await db.commit()

        # clean up task
        if self.user_id in self.running_tasks and pomodoro_id in self.running_tasks[self.user_id]:
            del self.running_tasks[self.user_id][pomodoro_id]

    async def stop(self, pomodoro_id: str, user_id: str):
        async with AsyncSessionLocal() as db:
            pomodoro = await self._get_pomodoro(pomodoro_id, user_id)
            
            if not pomodoro:
                return None
            if pomodoro.status == "completed":
                raise ValueError('Cannot play with a finished pomodoro.')
            if pomodoro.status == "stopped":
                raise ValueError('Pomodoro is already stopped.')
            
            print(f"CURRENT TASK: {asyncio.current_task()}")
            user_tasks = self.running_tasks.get(user_id, {})
            
            task =  int(pomodoro_id) if int(pomodoro_id) in user_tasks.keys() else None
            print(f"TASK to stop: {task}")
            if user_tasks[task]:
                print("CANCELLING TASKS!!!!")
                user_tasks[task].cancel()
                asyncio.current_task().cancelled
                try:
                    await user_tasks[task]
                except asyncio.CancelledError:
                    pass
            
            # Update worked time if pomo was running
            if pomodoro.status == "running" and pomodoro.last_resume_time:
                now = datetime.now()
                elapsed = (now - pomodoro.last_resume_time).total_seconds()
                pomodoro.worked_time += round(float(elapsed), 2)

            pomodoro.status = "stopped"
            pomodoro.end_time = datetime.now() 
            pomodoro.last_resume_time = None

            db.add(pomodoro)
            await db.commit()
            
            if pomodoro_id in self.running_tasks:
                del self.running_task[pomodoro_id]

            # clean up task
        if self.user_id in self.running_tasks and pomodoro_id in self.running_tasks[self.user_id]:
            del self.running_tasks[self.user_id][pomodoro_id]

        return pomodoro

    async def pause(self, pomodoro_id: str, user_id: str):
        async with AsyncSessionLocal() as db:
            pomodoro = await self._get_pomodoro(pomodoro_id, user_id)

            if not pomodoro:
                return None
            if pomodoro.status == "completed":
                raise ValueError('Cannot play with a finished pomodoro.')
            if pomodoro.status != "running":
                raise ValueError("Cannot pause a pomodoro that is not running.")
            
            if pomodoro.last_resume_time:
                now = datetime.now()
                elapsed = (now - pomodoro.last_resume_time).total_seconds()
                pomodoro.worked_time += round(float(elapsed), 2)

            pomodoro.status = "paused"
            pomodoro.last_resume_time = None

            db.add(pomodoro)
            await db.commit()

            user_tasks = self.running_tasks.get(user_id, {})
            task = user_tasks.get(pomodoro_id)

            # Cancel running task
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                finally:
                   # clean up task
                    if self.user_id in self.running_tasks and pomodoro_id in self.running_tasks[self.user_id]:
                        del self.running_tasks[self.user_id][pomodoro_id]

        return pomodoro

    async def resume(self, pomodoro_id: str, user_id: str):
        async with AsyncSessionLocal() as db:
            pomodoro = await self._get_pomodoro(pomodoro_id, user_id)

            if not pomodoro:
                return None
            if pomodoro.status == "completed":
                raise ValueError('Cannot play with a finished pomodoro.')
            if pomodoro.status == "running":
                raise ValueError('Pomodoro is already running.')
            if pomodoro.status == "stopped":
                raise ValueError('Cannot resume a pomodoro that was stopped.')

            pomodoro.status = "running"
            pomodoro.last_resume_time = datetime.now()

            db.add(pomodoro)
            await db.commit()

        # Start a new task from the paused pomodoro
        if user_id not in self.running_tasks:
            self.running_tasks[user_id] = {}

        task = asyncio.create_task(self.run_pomodoro(pomodoro_id))
        self.running_tasks[user_id][pomodoro_id] = task

        return pomodoro    

    '''async def extend(self, pomodoro_id: str, add_time: int):
        async with AsyncSessionLocal() as db:
            pomodoro = await self._get_pomodoro(pomodoro_id)

            if not pomodoro:
                return None
            if pomodoro.status == "completed":
                raise ValueError('Cannot play with a finished pomodoro.')
            if pomodoro.status == "stopped":
                raise ValueError('Cannot extend a pomodoro that was stopped.')
            
            pomodoro.timer += add_time.total_seconds()
            db.add(pomodoro)
            await db.commit()

        return pomodoro
'''
    async def _get_pomodoro(self, pomodoro_id: str, user_id: str):
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Pomodoro).where(
                    Pomodoro.id == int(pomodoro_id), 
                    Pomodoro.user_id == user_id
                )
            ) 
            
        return result.scalar_one_or_none()