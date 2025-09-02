from datetime import datetime, timedelta
from app.db.models.pomodoro import Pomodoro
from app.db.session import AsyncSessionLocal
from sqlalchemy.future import select
from sqlalchemy import update
import asyncio
from typing import Optional, Callable
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CancellableTimer:
    def __init__(self):
        self._cancel_event = asyncio.Event()
        self._current_task: Optional[asyncio.Task] = None

    async def cancellable_sleep(self, time: float) -> bool:
        """Cancellable asyncio sleep"""
        try:
            interval = 0.1  # Divide sleep in intervals for faster response
            elapsed = 0

            while elapsed < time:
                # Check if cancelled
                if self._cancel_event.is_set():
                    return False

                sleep_time = min(interval, time - elapsed)
                try: 
                    await asyncio.wait_for(asyncio.sleep(sleep_time), timeout=sleep_time + 0.1)
                except asyncio.TimeoutError:
                    pass

                elapsed += sleep_time
            
            return True

        except asyncio.CancelledError:
            return False
        
    async def run_timer(self, timer_duration: float, update_callback: Callable, update_interval: int = 5):
        """Run cancellable timer"""
        self._cancel_event.clear()

        try:
            elapsed = 0
            while elapsed < timer_duration:
                completed = await self.cancellable_sleep(1.0)
                if not completed:
                    break

                elapsed += 1

                if elapsed % update_interval == 0 or elapsed == timer_duration:
                    await update_callback(elapsed)
                
            if elapsed >= timer_duration:
                await update_callback(elapsed, completed=True)
            else: 
                await update_callback(elapsed, cancelled=True)

        except asyncio.CancelledError:
            await update_callback(elapsed, cancelled=True) 
            raise
    
    def cancel(self):
        """Cancel timer"""
        self._cancel_event.set()
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()

    async def start(self, duration: float, update_callback: Callable):
        """Start timer"""
        self._current_task = asyncio.create_task(
            self.run_timer(duration, update_callback)
        )
        return self._current_task

class PomodoroTimer:
    def __init__(self, user_id: str):
        self.user_id = user_id
        # map pomodoro_id to CancellableTimer
        self.timers: dict[int, CancellableTimer] = {}

    async def create_pomodoro(self, rest_time: int, task_name: str, timer: int = 25, status: str = "scheduled"):
        """Create a new pomodoro session"""
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
        
        logger.info(f"Created pomodoro {new_pomodoro.id} for user {self.user_id}")
        return new_pomodoro
    
    async def run_pomodoro(self, pomodoro_id: int, status: str = "running"):
        """Run a pomodoro timer"""
        try:
            # Get pomodoro details
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Pomodoro).
                    where(Pomodoro.id == pomodoro_id, Pomodoro.user_id == self.user_id),
                )

                pomodoro = result.scalar_one_or_none()
                 
                if not pomodoro:
                    logger.error(f"Pomodoro {pomodoro_id} not found for user {self.user_id}")
                    return
                
                # Update status to running
                await db.execute(
                    update(Pomodoro)
                    .where(Pomodoro.id == pomodoro_id, Pomodoro.user_id == self.user_id)
                    .values(status=status, last_resume_time=datetime.now())
                )
                await db.commit()
                
                timer_duration = pomodoro.timer
                
            # Create and store timer
            timer = CancellableTimer()
            self.timers[pomodoro_id] = timer

            async def update_callback(elapsed: int, completed=False, cancelled=False):
                """update progress with callback"""
                if completed:
                    logger.info(f"Pomodoro {pomodoro_id} completed")
                    await self.completed(pomodoro_id)
                elif cancelled:
                    logger.info(f"Pomodoro {pomodoro_id} cancelled")
                    await self.cancelled(pomodoro_id, elapsed)
                else:
                    # periodic update every 10 sec
                    if elapsed % 10 == 0:
                        await self.update_progress(pomodoro_id, elapsed)
            
            # Execute timer in background (non-blocking)
            asyncio.create_task(self._run_timer_with_cleanup(pomodoro_id, timer, timer_duration, update_callback))

        except asyncio.CancelledError:
            logger.info(f"Pomodoro {pomodoro_id} was cancelled.")
        except Exception as e:
            logger.error(f"Pomodoro {pomodoro_id} failed: {e}")
            await self.failed(pomodoro_id)

    async def _run_timer_with_cleanup(self, pomodoro_id: int, timer: CancellableTimer, duration: int, callback):
        """Run timer with proper cleanup"""
        try:
            await timer.start(duration, callback)
        except asyncio.CancelledError:
            logger.info(f"Pomodoro {pomodoro_id} cancelled")
        finally:
            self.stop(pomodoro_id)
            # Clean up timer reference
            '''if pomodoro_id in self.timers:
                del self.timers[pomodoro_id]'''

    async def update_progress(self, pomodoro_id: str, elapsed: int):
        """Update pomodoro progress"""
        try:
            async with AsyncSessionLocal() as db:
                await db.execute(
                    update(Pomodoro)
                    .where(Pomodoro.id == pomodoro_id, Pomodoro.user_id == self.user_id)
                    .values(worked_time=elapsed)
                )
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to update progress for pomodoro {pomodoro_id}: {e}")

    async def stop(self, pomodoro_id: int):
        """Stop pomodoro function"""
        try:
            # Cancel timer if running
            if pomodoro_id in self.timers:
                timer = self.timers[pomodoro_id]
                timer.cancel()

                # Wait for cleanup
                await asyncio.sleep(0.1)
                
                # Delete timer reference
                del self.timers[pomodoro_id]

            # Update database
            async with AsyncSessionLocal() as db:
                await db.execute(
                    update(Pomodoro)
                    .where(Pomodoro.id == pomodoro_id, Pomodoro.user_id == self.user_id)
                    .values(status='stopped', end_time=datetime.now())
                )
                await db.commit()
                
            logger.info(f"Pomodoro {pomodoro_id} stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop pomodoro {pomodoro_id}: {e}")
            raise

    async def completed(self, pomodoro_id: int):
        """When a pomodoro is successfully finished"""
        try:
            async with AsyncSessionLocal() as db:
                await db.execute(
                    update(Pomodoro)
                    .where(Pomodoro.id == pomodoro_id, Pomodoro.user_id == self.user_id)
                    .values(status='completed', end_time=datetime.now(), completed=True)
                )
                await db.commit()

            # Delete timer reference
            del self.timers[pomodoro_id]
                
            logger.info(f"Pomodoro {pomodoro_id} marked as completed")
            
        except Exception as e:
            logger.error(f"Failed to mark pomodoro {pomodoro_id} as completed: {e}")

    async def failed(self, pomodoro_id: int):
        """When a pomodoro execution fails"""
        try:
            async with AsyncSessionLocal() as db:
                await db.execute(
                    update(Pomodoro)
                    .where(Pomodoro.id == pomodoro_id, Pomodoro.user_id == self.user_id)
                    .values(status='failed')
                )
                await db.commit()
                
            logger.info(f"Pomodoro {pomodoro_id} marked as failed")
            
        except Exception as e:
            logger.error(f"Failed to mark pomodoro {pomodoro_id} as failed: {e}")

    async def cancelled(self, pomodoro_id: int, elapsed: int):
        """When a pomodoro is cancelled"""
        try:
            async with AsyncSessionLocal() as db:
                await db.execute(
                    update(Pomodoro)
                    .where(Pomodoro.id == pomodoro_id, Pomodoro.user_id == self.user_id)
                    .values(worked_time=elapsed, status='stopped', end_time=datetime.now())
                )
                await db.commit()
                
            logger.info(f"Pomodoro {pomodoro_id} cancelled at {elapsed} seconds")
            
        except Exception as e:
            logger.error(f"Failed to update cancelled pomodoro {pomodoro_id}: {e}")

    async def pause(self, pomodoro_id: int):
        """Pause a running pomodoro"""
        try:
            logger.info(f"Attempting to pause pomodoro {pomodoro_id} for user {self.user_id}")
            
            # First, get the pomodoro from database to check its current status
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Pomodoro).where(Pomodoro.id == pomodoro_id, Pomodoro.user_id == self.user_id)
                )
                pomodoro = result.scalar_one_or_none()
                
                if not pomodoro:
                    logger.error(f"Pomodoro {pomodoro_id} not found in database for user {self.user_id}")
                    raise ValueError("Pomodoro not found")

                logger.info(f"Pomodoro {pomodoro_id} current status: {pomodoro.status}")

                # Check if pomodoro can be paused based on its current status
                if pomodoro.status == "completed":
                    raise ValueError('Cannot pause a completed pomodoro.')
                if pomodoro.status == "paused":
                    raise ValueError('Pomodoro is already paused.')
                if pomodoro.status == "stopped":
                    raise ValueError('Cannot pause a stopped pomodoro.')
                if pomodoro.status != "running":
                    raise ValueError(f"Cannot pause a pomodoro with status '{pomodoro.status}'. Only running pomodoros can be paused.")

            # Check if timer is running in memory
            print(f"TIMERRS: {self.timers}")
            timer_in_memory = pomodoro_id in self.timers
            logger.info(f"Timer for pomodoro {pomodoro_id} in memory: {timer_in_memory}")
            
            if not timer_in_memory:
                # Timer not in memory but status is running - this indicates inconsistency
                # We should still allow pausing and clean up the database state
                logger.warning(f"Timer for pomodoro {pomodoro_id} not found in memory but status is '{pomodoro.status}'. Cleaning up database state.")
            else:
                # Cancel the running timer
                timer = self.timers[pomodoro_id]
                logger.info(f"Cancelling timer for pomodoro {pomodoro_id}")
                timer.cancel()
                
                # Wait for cleanup
                await asyncio.sleep(0.1)
                
                # Remove timer reference
                del self.timers[pomodoro_id]
                logger.info(f"Removed timer reference for pomodoro {pomodoro_id}")

            # Update database to paused state
            async with AsyncSessionLocal() as db:
                # Re-fetch to ensure we have the latest state
                result = await db.execute(
                    select(Pomodoro).where(Pomodoro.id == pomodoro_id, Pomodoro.user_id == self.user_id)
                )
                pomodoro = result.scalar_one_or_none()
                
                if not pomodoro:
                    raise ValueError("Pomodoro not found")

                # Calculate worked time since last resume
                if pomodoro.last_resume_time:
                    now = datetime.now()
                    elapsed = int((now - pomodoro.last_resume_time).total_seconds())
                    pomodoro.worked_time += elapsed
                    logger.info(f"Added {elapsed} seconds to worked time for pomodoro {pomodoro_id}")

                pomodoro.status = "paused"
                pomodoro.last_resume_time = None

                db.add(pomodoro)
                await db.commit()
                await db.refresh(pomodoro)
                
            logger.info(f"Successfully paused pomodoro {pomodoro_id} for user {self.user_id}")
            return pomodoro
            
        except Exception as e:
            logger.error(f"Failed to pause pomodoro {pomodoro_id} for user {self.user_id}: {e}")
            # Log current timer states for debugging
            self.log_timer_states()
            raise

    async def resume(self, pomodoro_id: int):
        """Resume a paused pomodoro"""
        try:
            # Check pomodoro status
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Pomodoro).where(Pomodoro.id == pomodoro_id, Pomodoro.user_id == self.user_id)
                )
                pomodoro = result.scalar_one_or_none()

                if not pomodoro:
                    raise ValueError("Pomodoro not found")
                if pomodoro.status == "completed":
                    raise ValueError('Cannot resume a completed pomodoro.')
                if pomodoro.status == "running":
                    raise ValueError('Pomodoro is already running.')
                if pomodoro.status == "stopped":
                    raise ValueError('Cannot resume a pomodoro that was stopped.')
                if pomodoro.status == "scheduled":
                    raise ValueError('Cannot resume a scheduled pomodoro. Start it first.')

                # Update status
                pomodoro.status = "running"
                pomodoro.last_resume_time = datetime.now()

                db.add(pomodoro)
                await db.commit()
                await db.refresh(pomodoro)

            # Start timer for remaining time
            remaining_time = pomodoro.timer - pomodoro.worked_time
            if remaining_time > 0:
                timer = CancellableTimer()
                self.timers[pomodoro_id] = timer

                async def update_callback(elapsed: int, completed=False, cancelled=False):
                    """Update progress with callback"""
                    total_elapsed = pomodoro.worked_time + elapsed
                    if completed:
                        logger.info(f"Pomodoro {pomodoro_id} completed")
                        await self.completed(pomodoro_id)
                    elif cancelled:
                        logger.info(f"Pomodoro {pomodoro_id} cancelled")
                        await self.cancelled(pomodoro_id, total_elapsed)
                    else:
                        # Periodic update every 10 seconds
                        if elapsed % 10 == 0:
                            await self.update_progress(pomodoro_id, total_elapsed)

                # Start timer for remaining time
                await timer.start(remaining_time, update_callback)
                
            logger.info(f"Pomodoro {pomodoro_id} resumed")
            return pomodoro
            
        except Exception as e:
            logger.error(f"Failed to resume pomodoro {pomodoro_id}: {e}")
            raise

    async def _get_pomodoro(self, pomodoro_id: int):
        """Get pomodoro by ID for current user"""
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Pomodoro).where(
                        Pomodoro.id == pomodoro_id, 
                        Pomodoro.user_id == self.user_id
                    )
                ) 
                
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get pomodoro {pomodoro_id}: {e}")
            return None

    def is_running(self, pomodoro_id: int) -> bool:
        """Check if a pomodoro timer is currently running"""
        return pomodoro_id in self.timers

    def get_running_pomodoros(self) -> list[int]:
        """Get list of currently running pomodoro IDs"""
        return list(self.timers.keys())

    async def check_state_consistency(self, pomodoro_id: int) -> dict:
        """Check if timer state and database status are consistent"""
        try:
            # Check in-memory timer state
            timer_running = pomodoro_id in self.timers
            
            # Check database status
            pomodoro = await self._get_pomodoro(pomodoro_id)
            if not pomodoro:
                return {
                    "pomodoro_id": pomodoro_id,
                    "timer_running": timer_running,
                    "database_status": None,
                    "consistent": False,
                    "issue": "Pomodoro not found in database"
                }
            
            database_running = pomodoro.status == "running"
            consistent = timer_running == database_running
            
            return {
                "pomodoro_id": pomodoro_id,
                "timer_running": timer_running,
                "database_status": pomodoro.status,
                "consistent": consistent,
                "issue": None if consistent else f"Timer running: {timer_running}, Database status: {pomodoro.status}"
            }
        except Exception as e:
            logger.error(f"Failed to check state consistency for pomodoro {pomodoro_id}: {e}")
            return {
                "pomodoro_id": pomodoro_id,
                "timer_running": False,
                "database_status": None,
                "consistent": False,
                "issue": f"Error checking consistency: {e}"
            }

    async def fix_inconsistent_state(self, pomodoro_id: int) -> bool:
        """Attempt to fix inconsistent state between timer and database"""
        try:
            consistency = await self.check_state_consistency(pomodoro_id)
            if consistency["consistent"]:
                return True
            
            pomodoro = await self._get_pomodoro(pomodoro_id)
            if not pomodoro:
                return False
            
            # If timer is running but database says not running, update database
            if consistency["timer_running"] and pomodoro.status != "running":
                logger.info(f"Fixing inconsistent state: Timer running but database status is '{pomodoro.status}' for pomodoro {pomodoro_id}")
                async with AsyncSessionLocal() as db:
                    await db.execute(
                        update(Pomodoro)
                        .where(Pomodoro.id == pomodoro_id, Pomodoro.user_id == self.user_id)
                        .values(status="running", last_resume_time=datetime.now())
                    )
                    await db.commit()
                return True
            
            # If database says running but timer is not, clean up database
            elif not consistency["timer_running"] and pomodoro.status == "running":
                logger.info(f"Fixing inconsistent state: Database status is 'running' but timer not running for pomodoro {pomodoro_id}")
                async with AsyncSessionLocal() as db:
                    await db.execute(
                        update(Pomodoro)
                        .where(Pomodoro.id == pomodoro_id, Pomodoro.user_id == self.user_id)
                        .values(status="stopped")
                    )
                    await db.commit()
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to fix inconsistent state for pomodoro {pomodoro_id}: {e}")
            return False

    async def cleanup_user_timers(self):
        """Clean up all timers for the current user"""
        try:
            for pomodoro_id in list(self.timers.keys()):
                if self.timers[pomodoro_id]:
                    self.timers[pomodoro_id].cancel()
                del self.timers[pomodoro_id]
            logger.info(f"Cleaned up all timers for user {self.user_id}")
        except Exception as e:
            logger.error(f"Failed to cleanup timers for user {self.user_id}: {e}")

    def log_timer_states(self):
        """Log the current state of all timers for debugging"""
        logger.info(f"User {self.user_id} timer states:")
        if not self.timers:
            logger.info("  No active timers")
        else:
            for pomodoro_id in self.timers:
                timer = self.timers[pomodoro_id]
                if timer:
                    logger.info(f"  Pomodoro {pomodoro_id}: Timer active")
                else:
                    logger.info(f"  Pomodoro {pomodoro_id}: Timer reference exists but is None")