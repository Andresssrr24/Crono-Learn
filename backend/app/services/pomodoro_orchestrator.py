from typing import Dict, List, Optional, Set
from app.services.pomodoro_timer import PomodoroTimer
from app.db.models.pomodoro import Pomodoro
from app.db.session import AsyncSessionLocal
from sqlalchemy.future import select
from sqlalchemy import update
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PomodoroOrchestrator:
    """
    Orchestrator service for managing multiple pomodoro sessions across users.
    Provides centralized management and coordination of pomodoro timers.
    """    
    def __init__(self):
        # Map user_id to their PomodoroTimer instance
        self.user_timers: Dict[str, PomodoroTimer] = {}
        # Track active pomodoro sessions per user
        self.active_sessions: Dict[str, Set[int]] = {}
        # Global lock
        self._lock = asyncio.Lock()
    
    async def get_user_timer(self, user_id: str) -> PomodoroTimer:
        """Get or create a PomodoroTimer instance for a user"""
        async with self._lock:
            if user_id not in self.user_timers:
                self.user_timers[user_id] = PomodoroTimer(user_id)
                self.active_sessions[user_id] = set()
                logger.info(f"Created new timer instance for user {user_id}")
            
            return self.user_timers[user_id]
    
    async def start_pomodoro(self, user_id: str, rest_time: int, task_name: str, timer: int = 25) -> Pomodoro:
        """Start a new pomodoro session for a user"""
        try:
            user_timer = await self.get_user_timer(user_id)
            
            # Create the pomodoro
            pomodoro = await user_timer.create_pomodoro(
                rest_time=rest_time,
                task_name=task_name,
                timer=timer,
                status="scheduled"
            )
            
            # Track the session
            self.active_sessions[user_id].add(pomodoro.id)
            
            # Start the timer in background
            asyncio.create_task(self._run_pomodoro_with_monitoring(user_id, pomodoro.id))
            
            logger.info(f"Started pomodoro {pomodoro.id} for user {user_id}")
            return pomodoro
            
        except Exception as e:
            logger.error(f"Failed to start pomodoro for user {user_id}: {e}")
            raise
    
    async def _run_pomodoro_with_monitoring(self, user_id: str, pomodoro_id: int):
        """Run a pomodoro with monitoring and cleanup"""
        try:
            user_timer = await self.get_user_timer(user_id)
            await user_timer.run_pomodoro(pomodoro_id)
        except Exception as e:
            logger.error(f"Error running pomodoro {pomodoro_id} for user {user_id}: {e}")
            # Mark as failed
            try:
                await user_timer.failed(pomodoro_id)
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup failed pomodoro {pomodoro_id}: {cleanup_error}")
        finally:
            # Clean up session tracking
            async with self._lock:
                if user_id in self.active_sessions:
                    self.active_sessions[user_id].discard(pomodoro_id)
    
    async def pause_pomodoro(self, user_id: str, pomodoro_id: int) -> Pomodoro:
        """Pause a running pomodoro"""
        try:
            user_timer = await self.get_user_timer(user_id)
            pomodoro = await user_timer.pause(pomodoro_id)
            
            # Update session tracking
            if user_id in self.active_sessions:
                self.active_sessions[user_id].discard(pomodoro_id)
            
            logger.info(f"Paused pomodoro {pomodoro_id} for user {user_id}")
            return pomodoro
            
        except Exception as e:
            logger.error(f"Failed to pause pomodoro {pomodoro_id} for user {user_id}: {e}")
            raise
    
    async def resume_pomodoro(self, user_id: str, pomodoro_id: int) -> Pomodoro:
        """Resume a paused pomodoro"""
        try:
            user_timer = await self.get_user_timer(user_id)
            pomodoro = await user_timer.resume(pomodoro_id)
            
            # Track the session again
            self.active_sessions[user_id].add(pomodoro.id)
            
            # Start monitoring the resumed pomodoro
            asyncio.create_task(self._run_pomodoro_with_monitoring(user_id, pomodoro.id))
            
            logger.info(f"Resumed pomodoro {pomodoro_id} for user {user_id}")
            return pomodoro
            
        except Exception as e:
            logger.error(f"Failed to resume pomodoro {pomodoro_id} for user {user_id}: {e}")
            raise
    
    async def stop_pomodoro(self, user_id: str, pomodoro_id: int) -> Pomodoro:
        """Stop a pomodoro session"""
        try:
            user_timer = await self.get_user_timer(user_id)
            await user_timer.stop(pomodoro_id)
            
            # Clean up session tracking
            if user_id in self.active_sessions:
                self.active_sessions[user_id].discard(pomodoro_id)
            
            # Get updated pomodoro
            pomodoro = await user_timer._get_pomodoro(pomodoro_id)
            
            logger.info(f"Stopped pomodoro {pomodoro_id} for user {user_id}")
            return pomodoro
            
        except Exception as e:
            logger.error(f"Failed to stop pomodoro {pomodoro_id} for user {user_id}: {e}")
            raise
    
    async def get_pomodoro_status(self, user_id: str, pomodoro_id: int) -> dict:
        """Get comprehensive status of a pomodoro"""
        try:
            user_timer = await self.get_user_timer(user_id)
            
            # Check if timer is running
            is_running = user_timer.is_running(pomodoro_id)
            
            # Get pomodoro details
            pomodoro = await user_timer._get_pomodoro(pomodoro_id)
            if not pomodoro:
                raise ValueError("Pomodoro not found")
            
            # Check if it's in active sessions
            is_active = pomodoro_id in self.active_sessions.get(user_id, set())
            
            return {
                "pomodoro_id": pomodoro_id,
                "status": pomodoro.status,
                "is_running": is_running,
                "is_active": is_active,
                "worked_time": pomodoro.worked_time,
                "timer": pomodoro.timer,
                "remaining_time": max(0, pomodoro.timer - pomodoro.worked_time),
                "task_name": pomodoro.task_name,
                "start_time": pomodoro.start_time,
                "last_resume_time": pomodoro.last_resume_time
            }
            
        except Exception as e:
            logger.error(f"Failed to get status for pomodoro {pomodoro_id}: {e}")
            raise
    
    async def get_user_pomodoros(self, user_id: str, status: Optional[str] = None) -> List[Pomodoro]:
        """Get all pomodoros for a user, optionally filtered by status"""
        try:
            async with AsyncSessionLocal() as db:
                query = select(Pomodoro).where(Pomodoro.user_id == user_id)
                if status:
                    query = query.where(Pomodoro.status == status)
                
                result = await db.execute(query)
                pomodoros = result.scalars().all()
                
                return list(pomodoros)
                
        except Exception as e:
            logger.error(f"Failed to get pomodoros for user {user_id}: {e}")
            raise

    async def check_pomodoro_state_consistency(self, user_id: str, pomodoro_id: int) -> dict:
        """Check if a pomodoro's state is consistent between timer and database"""
        try:
            user_timer = await self.get_user_timer(user_id)
            return await user_timer.check_state_consistency(pomodoro_id)
        except Exception as e:
            logger.error(f"Failed to check state consistency for pomodoro {pomodoro_id}: {e}")
            raise

    async def fix_pomodoro_state_consistency(self, user_id: str, pomodoro_id: int) -> bool:
        """Attempt to fix inconsistent state for a pomodoro"""
        try:
            user_timer = await self.get_user_timer(user_id)
            return await user_timer.fix_inconsistent_state(pomodoro_id)
        except Exception as e:
            logger.error(f"Failed to fix state consistency for pomodoro {pomodoro_id}: {e}")
            raise

    async def get_running_pomodoros(self, user_id: str) -> List[Pomodoro]:
        """Get all currently running pomodoros for a user"""
        try:
            user_timer = await self.get_user_timer(user_id)
            running_ids = user_timer.get_running_pomodoros()
            
            running_pomodoros = []
            for pomodoro_id in running_ids:
                pomodoro = await user_timer._get_pomodoro(pomodoro_id)
                if pomodoro:
                    running_pomodoros.append({
                        "id": pomodoro.id,
                        "task_name": pomodoro.task_name,
                        "timer": pomodoro.timer,
                        "worked_time": pomodoro.worked_time,
                        "remaining_time": max(0, pomodoro.timer - pomodoro.worked_time),
                        "start_time": pomodoro.start_time,
                        "status": pomodoro.status
                    })
            
            return running_pomodoros
            
        except Exception as e:
            logger.error(f"Failed to get running pomodoros for user {user_id}: {e}")
            raise
    
    async def cleanup_user_sessions(self, user_id: str):
        """Clean up all sessions and timers for a user"""
        try:
            async with self._lock:
                if user_id in self.user_timers:
                    # Stop all running timers
                    user_timer = self.user_timers[user_id]
                    await user_timer.cleanup_user_timers()
                    
                    # Clean up active sessions
                    if user_id in self.active_sessions:
                        self.active_sessions[user_id].clear()
                    
                    # Remove user timer instance
                    del self.user_timers[user_id]
                    
                    logger.info(f"Cleaned up all sessions for user {user_id}")
                    
        except Exception as e:
            logger.error(f"Failed to cleanup sessions for user {user_id}: {e}")
            raise
    
    async def get_system_stats(self) -> dict:
        """Get system-wide statistics"""
        try:
            async with self._lock:
                total_users = len(self.user_timers)
                total_active_sessions = sum(len(sessions) for sessions in self.active_sessions.values())
                
                # Get database stats
                async with AsyncSessionLocal() as db:
                    # Total pomodoros
                    result = await db.execute(select(Pomodoro))
                    total_pomodoros = len(result.scalars().all())
                    
                    # Completed pomodoros
                    result = await db.execute(select(Pomodoro).where(Pomodoro.status == "completed"))
                    completed_pomodoros = len(result.scalars().all())
                    
                    # Running pomodoros
                    result = await db.execute(select(Pomodoro).where(Pomodoro.status == "running"))
                    running_pomodoros = len(result.scalars().all())
                
                return {
                    "total_users": total_users,
                    "total_active_sessions": total_active_sessions,
                    "total_pomodoros": total_pomodoros,
                    "completed_pomodoros": completed_pomodoros,
                    "running_pomodoros": running_pomodoros,
                    "active_users": len([uid for uid, sessions in self.active_sessions.items() if sessions])
                }
                
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            raise
    
    async def health_check(self) -> dict:
        """Perform a health check of the orchestrator"""
        try:
            # Check if all user timers are responsive
            health_status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "user_timers_count": len(self.user_timers),
                "active_sessions_count": sum(len(sessions) for sessions in self.active_sessions.values()),
                "issues": []
            }
            
            # Check for any orphaned sessions
            for user_id, sessions in self.active_sessions.items():
                if user_id not in self.user_timers:
                    health_status["issues"].append(f"Orphaned sessions for user {user_id}")
                    health_status["status"] = "degraded"
            
            # Check for any running timers without active sessions
            for user_id, user_timer in self.user_timers.items():
                running_ids = user_timer.get_running_pomodoros()
                active_sessions = self.active_sessions.get(user_id, set())
                
                for running_id in running_ids:
                    if running_id not in active_sessions:
                        health_status["issues"].append(f"Running timer {running_id} without active session for user {user_id}")
                        health_status["status"] = "degraded"
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

# Global orchestrator instance
pomodoro_orchestrator = PomodoroOrchestrator()
