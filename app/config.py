from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/testdb"
    secret_key: str = "gfdmhghif38yrf9ew0jkf32"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
