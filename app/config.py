from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    database_url: str = Field(
        validation_alias=AliasChoices("DATABASE_URL", "DB_CONNECTION")
    )
    redis_url: str = "redis://localhost:6379/0"
    llm_provider: str = "openai"
    openai_api_key: str
    llm_model: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
