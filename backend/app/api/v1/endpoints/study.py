from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.study_service import StudyService
from app.schemas.study import StudyCreate, StudyResponse
from .user import get_current_user_email

router = APIRouter(tags=['Study'])

@router.post('/', response_model=StudyResponse, status_code=status.HTTP_201_CREATED)
async def create_study_record(data: StudyCreate, db: AsyncSession = Depends(get_db), email: str = Depends(get_current_user_email)):
    service = StudyService(db, user_email=email)
    study_record = await service.create_study_record(email=email, data=data)
    return study_record

@router.get('/', response_model=list[StudyResponse])
async def get_study_records(db: AsyncSession = Depends(get_db), email: str = Depends(get_current_user_email)):
    service = StudyService(db, user_email=email)
    study_records = await service.get_study_records()
    return study_records, {"message": "Study records retrieved successfully"}
