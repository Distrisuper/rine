from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(
        default="sqlite:////app/.data/rine.db",
        alias="DATABASE_URL",
    )
    invoice_base_url: str | None = Field(default=None, alias="INVOICE_BASE_URL")
    admin_security_code: str = Field(default="rine01", alias="ADMIN_SECURITY_CODE")
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
