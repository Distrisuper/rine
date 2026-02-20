from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

import aiosqlite

from app.interfaces.print_job_repository import PrintJobRepository
from app.models import PrintJobRecord, PrintJobStatus, PrintRequest


class SqliteRepository(PrintJobRepository):
    """Repositorio SQLite para trabajos de impresion."""

    def __init__(self, db_path: str):
        self._db_path = db_path

    async def initialize(self) -> None:
        """Crea tablas e indices si no existen."""
        async with self._connection() as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS print_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id TEXT,
                    client_code TEXT NOT NULL,
                    client_name TEXT NOT NULL,
                    print_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    print_count INTEGER NOT NULL,
                    host INTEGER,
                    date_created TEXT NOT NULL,
                    date_started TEXT,
                    date_processed TEXT,
                    payload TEXT NOT NULL
                )
                """
            )
            await db.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_print_jobs_status_created
                ON print_jobs(status, date_created)
                """
            )
            await db.commit()

    async def enqueue_job(
        self,
        request: PrintRequest,
        status: PrintJobStatus,
        created_at: str,
        print_count: int,
        payload: str,
    ) -> PrintJobRecord:
        """Encola un trabajo de impresion."""
        async with self._connection() as db:
            cursor = await db.execute(
                """
                INSERT INTO print_jobs (
                    client_id,
                    client_code,
                    client_name,
                    print_type,
                    status,
                    print_count,
                    host,
                    date_created,
                    date_started,
                    date_processed,
                    payload
                ) VALUES (
                    :client_id,
                    :client_code,
                    :client_name,
                    :print_type,
                    :status,
                    :print_count,
                    :host,
                    :date_created,
                    :date_started,
                    :date_processed,
                    :payload
                )
                """,
                {
                    "client_id": None,
                    "client_code": request.client_code,
                    "client_name": request.client_name,
                    "print_type": request.type,
                    "location": request.location,
                    "status": status.value,
                    "print_count": print_count,
                    "host": request.set_host,
                    "date_created": created_at,
                    "date_started": None,
                    "date_processed": None,
                    "payload": payload,
                },
            )
            await db.commit()
            job_id = cursor.lastrowid

        return PrintJobRecord(
            id=int(job_id),
            status=status,
            date_created=created_at,
            date_processed=None,
        )

    @asynccontextmanager
    async def _connection(self) -> aiosqlite.Connection:
        if self._db_path != ":memory:":
            db_path = Path(self._db_path)
            if db_path.parent.as_posix() not in (".", ""):
                db_path.parent.mkdir(parents=True, exist_ok=True)

        db = await aiosqlite.connect(self._db_path)
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA foreign_keys = ON")
        try:
            yield db
        finally:
            await db.close()

