from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, ExpiredSignatureError
import os

security = HTTPBearer()

SUPABASE_JWK_SECRET=os.getenv("SUPABASE_JWT_SECRET")
if not SUPABASE_JWK_SECRET:
    raise RuntimeError("SUPABASE_JWK_SECRET must be set on env variables.")

async def get_current_user_id(credentials: HTTPAuthorizationCredentials=Depends(security)):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SUPABASE_JWK_SECRET, algorithms=['HS256'], options={"verify_aud": False})
        return payload['sub']
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError as e:
        print("JWT error:", str(e))
        raise HTTPException(status_code=401, detail="Invalid token")
