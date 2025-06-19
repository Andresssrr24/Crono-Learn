from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.pomodoro_timer import PomodoroTimer
from app.schemas.pomodoro import PomodoroCreate, PomodoroResponse
from .user import get_current_user_email

router = APIRouter(tags=['Pomodoros'])

@router.post('/', response_model=PomodoroResponse, status_code=status.HTTP_201_CREATED)
async def start_pomodoro(data: PomodoroCreate, db: AsyncSession = Depends(get_db), email: str = Depends(get_current_user_email)):
    service = PomodoroTimer(db)
    pomodoro = await service.create_pomodoro(email=email, data=data)
    return pomodoro

@router.post('/{pomodoro_id}/pause', response_model=PomodoroResponse)
async def pause_pomodoro(pomodoro_id: str, db: AsyncSession = Depends(get_db), email: str = Depends(get_current_user_email)):
    service = PomodoroTimer(db)
    pomodoro = await service.pause(pomodoro_id=pomodoro_id, email=email)
    if not pomodoro:
        raise HTTPException(status_code=404, detail="Could not found pomodoro or user is not authorized")
    return pomodoro

@router.post('/{pomodoro_id}/stop', response_model=PomodoroResponse)
async def stop_pomodoro(pomodoro_id: str, db: AsyncSession = Depends(get_db), email: str = Depends(get_current_user_email)):
    service = PomodoroTimer(db)
    pomodoro = await service.stop(pomodoro_id=pomodoro_id, email=email)
    if not pomodoro:
        raise HTTPException(status_code=404, detail="Could not found pomodoro or user is not authorized")
    return pomodoro

@router.get('/')
async def test():
    return {"message": "Pomodoro endpoint is working"}