from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate
from app.crud.crud_user import create_user, get_users, get_user_by_id
from app.db.session import get_db

router = APIRouter(prefix='/users', tags=['Users'])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: AsyncSession=Depends(get_db)):
    return await create_user(db, user)