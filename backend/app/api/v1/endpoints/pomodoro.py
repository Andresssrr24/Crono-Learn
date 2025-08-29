from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.services.pomodoro_timer import PomodoroTimer
from app.services.pomodoro_orchestrator import pomodoro_orchestrator
from app.schemas.pomodoro import PomodoroCreate, PomodoroResponse, PomodoroUpdate
from app.db.models.pomodoro import Pomodoro
from app.core.auth import get_current_user_id
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=['Pomodoros'])

@router.options("/")
async def options_handler():
    return {"message": "CORS preflight"}

@router.post('/', response_model=PomodoroResponse, status_code=status.HTTP_201_CREATED)
async def start_pomodoro(data: PomodoroCreate, user_id: str = Depends(get_current_user_id)):
    """Start a new pomodoro session"""
    try:
        # Use orchestrator to start pomodoro
        pomodoro = await pomodoro_orchestrator.start_pomodoro(
            user_id=user_id,
            rest_time=data.rest_time, 
            task_name=data.task_name, 
            timer=data.timer
        )
        
        logger.info(f"Started pomodoro {pomodoro.id} for user {user_id}")
        return pomodoro
        
    except ValueError as e:
        logger.error(f"Validation error starting pomodoro: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting pomodoro: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to start pomodoro")

@router.get('/{pomodoro_id}', response_model=PomodoroResponse)
async def get_pomodoro(pomodoro_id: int, user_id: str = Depends(get_current_user_id)):
    """Get a specific pomodoro by ID"""
    try:
        # Use orchestrator to get pomodoro status
        status_info = await pomodoro_orchestrator.get_pomodoro_status(user_id, pomodoro_id)
        
        # Get full pomodoro details
        user_timer = await pomodoro_orchestrator.get_user_timer(user_id)
        pomodoro = await user_timer._get_pomodoro(pomodoro_id)

        if not pomodoro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Pomodoro not found"
            )
        
        return pomodoro

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error getting pomodoro {pomodoro_id}: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting pomodoro {pomodoro_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error"
        )

@router.patch("/{pomodoro_id}", response_model=PomodoroResponse)
async def update_pomodoro(pomodoro_id: int, data: PomodoroUpdate, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """Update a pomodoro session"""
    try:
        # Check if pomodoro exists and belongs to user
        result = await db.execute(
            select(Pomodoro).where(
                Pomodoro.id == pomodoro_id, 
                Pomodoro.user_id == user_id
            )
        )
        pomodoro = result.scalar_one_or_none()

        if not pomodoro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Pomodoro not found"
            )
        
        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(pomodoro, field, value)
        
        await db.commit() 
        await db.refresh(pomodoro)
        
        logger.info(f"Updated pomodoro {pomodoro_id} for user {user_id}")
        return pomodoro
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating pomodoro {pomodoro_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to update pomodoro"
        )

@router.post('/{pomodoro_id}/pause', response_model=PomodoroResponse)
async def pause_pomodoro(
    pomodoro_id: int, 
    user_id: str = Depends(get_current_user_id)
):
    """Pause a running pomodoro"""
    try:
        pomodoro = await pomodoro_orchestrator.pause_pomodoro(user_id, pomodoro_id)
        
        logger.info(f"Paused pomodoro {pomodoro_id} for user {user_id}")
        return pomodoro
        
    except ValueError as e:
        logger.error(f"Validation error pausing pomodoro {pomodoro_id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error pausing pomodoro {pomodoro_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to pause pomodoro"
        )

@router.post('/{pomodoro_id}/stop', response_model=PomodoroResponse)
async def stop_pomodoro(
    pomodoro_id: int, 
    user_id: str = Depends(get_current_user_id)
):
    """Stop a pomodoro session"""
    try:
        pomodoro = await pomodoro_orchestrator.stop_pomodoro(user_id, pomodoro_id)
        
        logger.info(f"Stopped pomodoro {pomodoro_id} for user {user_id}")
        return pomodoro
        
    except ValueError as e:
        logger.error(f"Validation error stopping pomodoro {pomodoro_id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error stopping pomodoro {pomodoro_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to stop pomodoro"
        )

@router.post("/{pomodoro_id}/resume", response_model=PomodoroResponse)
async def resume_pomodoro(
    pomodoro_id: int, 
    user_id: str = Depends(get_current_user_id)
):
    """Resume a paused pomodoro"""
    try:
        pomodoro = await pomodoro_orchestrator.resume_pomodoro(user_id, pomodoro_id)
        
        logger.info(f"Resumed pomodoro {pomodoro_id} for user {user_id}")
        return pomodoro
        
    except ValueError as e:
        logger.error(f"Validation error resuming pomodoro {pomodoro_id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error resuming pomodoro {pomodoro_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to resume pomodoro"
        )

@router.get('/{pomodoro_id}/status')
async def get_pomodoro_status(
    pomodoro_id: int, 
    user_id: str = Depends(get_current_user_id)
):
    """Get the current status of a pomodoro"""
    try:
        status_info = await pomodoro_orchestrator.get_pomodoro_status(user_id, pomodoro_id)
        return status_info
        
    except ValueError as e:
        logger.error(f"Validation error getting status for pomodoro {pomodoro_id}: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting status for pomodoro {pomodoro_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to get pomodoro status"
        )

@router.get('/user/running')
async def get_running_pomodoros(
    user_id: str = Depends(get_current_user_id)
):
    """Get all currently running pomodoros for a user"""
    try:
        running_pomodoros = await pomodoro_orchestrator.get_running_pomodoros(user_id)
        return {"running_pomodoros": running_pomodoros, "count": len(running_pomodoros)}
        
    except Exception as e:
        logger.error(f"Error getting running pomodoros for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to get running pomodoros"
        )

@router.get('/{pomodoro_id}/debug/consistency')
async def check_pomodoro_consistency(
    pomodoro_id: int,
    user_id: str = Depends(get_current_user_id)
):
    """Check if a pomodoro's state is consistent between timer and database"""
    try:
        consistency_info = await pomodoro_orchestrator.check_pomodoro_state_consistency(user_id, pomodoro_id)
        return consistency_info
        
    except Exception as e:
        logger.error(f"Error checking consistency for pomodoro {pomodoro_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to check pomodoro consistency"
        )

@router.post('/{pomodoro_id}/debug/fix-consistency')
async def fix_pomodoro_consistency(
    pomodoro_id: int,
    user_id: str = Depends(get_current_user_id)
):
    """Attempt to fix inconsistent state for a pomodoro"""
    try:
        fixed = await pomodoro_orchestrator.fix_pomodoro_state_consistency(user_id, pomodoro_id)
        return {"pomodoro_id": pomodoro_id, "fixed": fixed}
        
    except Exception as e:
        logger.error(f"Error fixing consistency for pomodoro {pomodoro_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to fix pomodoro consistency"
        )

@router.get('/user/all')
async def get_user_pomodoros(
    user_id: str = Depends(get_current_user_id),
    status: str = None
):
    """Get all pomodoros for a user, optionally filtered by status"""
    try:
        pomodoros = await pomodoro_orchestrator.get_user_pomodoros(user_id, status)
        return {"pomodoros": pomodoros, "count": len(pomodoros)}
        
    except Exception as e:
        logger.error(f"Error getting pomodoros for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to get user pomodoros"
        )

@router.delete('/user/cleanup')
async def cleanup_user_sessions(
    user_id: str = Depends(get_current_user_id)
):
    """Clean up all sessions and timers for a user"""
    try:
        await pomodoro_orchestrator.cleanup_user_sessions(user_id)
        return {"message": "User sessions cleaned up successfully"}
        
    except Exception as e:
        logger.error(f"Error cleaning up sessions for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to cleanup user sessions"
        )

# Admin endpoints for system monitoring
@router.get('/admin/stats')
async def get_system_stats(
    user_id: str = Depends(get_current_user_id)
):
    """Get system-wide statistics (admin only)"""
    try:
        # TODO: Add admin role check here
        stats = await pomodoro_orchestrator.get_system_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to get system stats"
        )

@router.get('/admin/health')
async def health_check(
    user_id: str = Depends(get_current_user_id)
):
    """Perform a health check of the orchestrator (admin only)"""
    try:
        # TODO: Add admin role check here
        health = await pomodoro_orchestrator.health_check()
        return health
        
    except Exception as e:
        logger.error(f"Error performing health check: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to perform health check"
        )