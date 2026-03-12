from functools import lru_cache

from sqlmodel import SQLModel, create_engine

from infrastructure.config import Settings, get_settings


@lru_cache
def get_engine() -> create_engine:
    settings = get_settings()
    return create_engine(settings.database_url, echo=False)


engine = get_engine()
