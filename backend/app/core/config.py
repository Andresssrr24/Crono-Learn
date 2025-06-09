from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str =  "CronoLearn API"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379"

    class Config:
        env_file = '/Users/Admin/Documents/Crono-Learn/backend/.env'
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()