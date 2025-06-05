from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str =  "CronoLearn API"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    BATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379"

    class Config:
        env_file = '.env'

@lru_cache()
def get_settings():
    return Settings()