from fastapi import APIRouter, Depends, status, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserOut
from app.crud.crud_user import create_user_if_not_exists
from app.db.session import get_db
import httpx
import os

router = APIRouter(tags=['Users'])

SUPABASE_PROJ_ID = 'yejmesbnspombdethdxt'
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

async def get_current_user_email(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")

    token = auth_header.split(" ")[1]
    async with httpx.AsyncClient() as client:
        response = await client.get(            
            f"https://{SUPABASE_PROJ_ID}.supabase.co/auth/v1/user",
            headers={"Authorization": f"Bearer {token}"}
            )

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid Supabase token")
    
    user_data = response.json()
    email = user_data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email not found in Supabase data")

    return email

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(db: AsyncSession=Depends(get_db), email: str=Depends(get_current_user_email)):
    return await create_user_if_not_exists(db, email=email)