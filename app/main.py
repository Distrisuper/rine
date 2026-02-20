from fastapi import FastAPI

from app.adapters.sqlite_repository import SqliteRepository
from app.api.routes import router
from app.config import get_settings

app = FastAPI()
app.include_router(router)


@app.on_event("startup")
async def startup_event() -> None:
	settings = get_settings()
	repository = SqliteRepository(settings.sqlite_db_path)
	await repository.initialize()