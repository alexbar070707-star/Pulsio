from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    app_name: str = "Pulsio"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database
    database_url: str

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Auth
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Anthropic
    anthropic_api_key: str

    # Quality gate
    min_quality_score: float = 0.6

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
