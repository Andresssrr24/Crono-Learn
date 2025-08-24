from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.services.pomodoro_timer import PomodoroTimer
from app.schemas.pomodoro import PomodoroCreate, PomodoroResponse, PomodoroUpdate
from app.db.models.pomodoro import Pomodoro
from app.core.auth import get_current_user_id

router = APIRouter(tags=['Pomodoros'])
@router.options("/")
async def options_handler():
    return {"message": "CORS preflight"}


@router.post('/', response_model=PomodoroResponse, status_code=status.HTTP_201_CREATED)
async def start_pomodoro(data: PomodoroCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    service = PomodoroTimer(user_id=user_id)
    pomodoro = await service.create_pomodoro(rest_time=data.rest_time, task_name=data.task_name, timer=data.timer)
    
    background_tasks.add_task(service.run_pomodoro, pomodoro.id)

    return pomodoro

@router.get('/{pomodoro_id}', response_model=PomodoroResponse)
async def get_pomodoro(pomodoro_id: str, user_id: str = Depends(get_current_user_id)):
    try:
        pomodoro_timer = PomodoroTimer(user_id=user_id)
        pomodoro = await pomodoro_timer._get_pomodoro(pomodoro_id=pomodoro_id, user_id=user_id)

        if not pomodoro:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pomodoro not found")
        if pomodoro.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        return pomodoro

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.patch("/{pomodoro_id}", response_model=PomodoroResponse)
async def update_pomodoro(pomodoro_id: str, data: PomodoroUpdate, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    result = await db.execute(select(Pomodoro).where(Pomodoro.id == pomodoro_id, Pomodoro.user_id == user_id))
    pomodoro = result.scalar_one_or_none()

    if not pomodoro:
        raise HTTPException(status_code=404, detail="Pomodoro not found")
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(pomodoro, field, value)
    
    await db.commit() 
    await db.refresh(pomodoro)
    return pomodoro 

@router.post('/{pomodoro_id}/pause', response_model=PomodoroResponse)
async def pause_pomodoro(pomodoro_id: str, background_tasks: BackgroundTasks, user_id: str = Depends(get_current_user_id)):
    service = PomodoroTimer(user_id=user_id)
    pomodoro = await service.pause(pomodoro_id=pomodoro_id, user_id=user_id)
    if not pomodoro:
        raise HTTPException(status_code=404, detail="Could not found pomodoro or user is not authorized")
    
    return pomodoro

@router.post('/{pomodoro_id}/stop', response_model=PomodoroResponse)
async def stop_pomodoro(pomodoro_id: str, background_tasks: BackgroundTasks, user_id: str = Depends(get_current_user_id)):
    service = PomodoroTimer(user_id=user_id)
    pomodoro = await service.stop(pomodoro_id=pomodoro_id, user_id=user_id)
    if not pomodoro:
        raise HTTPException(status_code=404, detail="Could not found pomodoro or user is not authorized")
    return pomodoro

@router.post("/{pomodoro_id}/resume", response_model=PomodoroResponse)
async def resume_pomodoro(pomodoro_id: str, background_tasks: BackgroundTasks, user_id: str = Depends(get_current_user_id)):
    service = PomodoroTimer(user_id=user_id)
    pomodoro = await service.resume(pomodoro_id=pomodoro_id, user_id=user_id)
    if not pomodoro:
        raise HTTPException(status_code=404, detail="Could not found pomodoro or user is not authorized")
    return pomodoro